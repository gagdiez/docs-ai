# BUILD VECTOR STORE FROM FILES
import json
import openai
import os
import re 
from glob import glob
from urllib.parse import urlparse
import requests
from nearai.shared.client_config import ClientConfig
from nearai.config import Config, load_config_file

# ---------------- Load NEAR AI Hub configuration
CONFIG = Config()
config_data = load_config_file(local=False)
CONFIG = CONFIG.update_with(config_data)

if CONFIG.api_url is None:
    raise ValueError("CONFIG.api_url is None")

base_url = CONFIG.api_url + "/v1"
client_config = ClientConfig(base_url=base_url, auth=CONFIG.auth)

client = openai.OpenAI(base_url=base_url, api_key=json.dumps(config_data["auth"]))

# Upload and attach add files to the vector store, skip existing vector-store doc file

def derive_url(paths: str, content: str) -> str:
    id = re.search(r'id: (.*)', content)
    id = id.group(1) if id else os.path.basename(paths).replace(".md", "")
    url_path = os.path.split(file_path)[0][2:] # remove the leading ./
    if 'concepts' not in url_path and 'tools' not in url_path: url_path = 'build/' + url_path
    return f"https://docs.near.org/docs/{url_path}/{id}"

def replace_github_with_code(content: str) -> str:
    # Find all the <Github language="" url="" /> tags and replace them with the actual code
    # <Github fname="keys.rs" language="rust" url="https://github.com/PiVortex/near-api-examples/tree/main/rust/examples/keys.rs#L43-L62" start="43" end="62" />
    githubs = re.findall(r"<Github\s[^>]*?/>", content)
    formatted = content
    for gh in githubs:
        gh = gh.replace("'", '"')
        url = re.search(r'url="(.*?)"', gh).group(1)

        (url, *loc) = url.split("#")
        (org, repo, blob, branch, *pathSeg) = urlparse(url).path[1:].split("/")
        pathSeg = "/".join(pathSeg)
        raw_url = f"https://raw.githubusercontent.com/{org}/{repo}/{branch}/{pathSeg}"
        res = requests.get(raw_url)
        code = res.text

        # cut based on the line numbers
        start = re.search(r'start="(\d*)"', gh)
        end = re.search(r'end="(\d*)"', gh)

        start = max(int(start.group(1)) - 1, 0) if start else 0
        end = int(end.group(1)) + 1 if end else len(code.split("\n"))
        code = "\n".join(code.split("\n")[start:end])

        formatted = formatted.replace(gh, f"```\n{code}\n```")

    return formatted

c2id = {}
id2url = {}

categories = [dir for dir in glob("*") if os.path.isdir(dir)]

for c in ['tools']:
    # Create a vector store for vector store docs
    vs = client.beta.vector_stores.create(name=f"{c}-vector")
    md_files = [file for file in glob(f"./{c}/**/*.md", recursive=True)]

    for file_path in md_files:
        print(f"Processing {c} {os.path.basename(file_path)}")
        with open(file_path, 'r') as file:
            content = file.read()
            formatted = replace_github_with_code(content)
            file_id = derive_url(file_path, content)
            print(f"\tfile id: {file_id}")

            client.beta.vector_stores
            uploaded_file = client.files.create(
                file=(file_path, formatted, "text/markdown"),
                purpose="assistants",
            )
            attached_file = client.beta.vector_stores.files.create(
                vector_store_id=vs.id,
                file_id=uploaded_file.id,
            )
            id2url[uploaded_file.id] = file_id
            print(f"\tfile uploaded")

        c2id[c] = vs.id

map2map = {
    'tools': 'tools',
    'web3-apps': 'integration',
    'chain-abstraction': 'abstraction',
    'data-infrastructure': 'infrastructure',
    'primitives': 'primitives',
    'concepts': 'concepts',
    'smart-contracts': 'contracts'
}

print(c2id)
print(id2url)

# tags2vid = {v: c2id[k] for k, v in map2map.items()}

# json.dump(tags2vid, open("../tags2vid.json", "w"))
# json.dump(id2url, open("../id2url.json", "w"))

