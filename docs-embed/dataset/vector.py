# BUILD VECTOR STORE FROM FILES
import json
import openai
import os
import re 
import pandas as pd
import requests

from glob import glob
from urllib.parse import urlparse
from nearai.shared.client_config import ClientConfig
from nearai.config import Config, load_config_file

embeddings_model = "fireworks::nomic-ai/nomic-embed-text-v1.5"
prefix = "classification: "

def derive_url(paths: str, content: str) -> str:
    id = re.search(r'id: (.*)', content)
    id = id.group(1) if id else os.path.basename(paths).replace(".md", "")
    url_path = os.path.split(file_path)[0][2:] # remove the leading ./
    if 'concepts' not in url_path and 'tools' not in url_path: url_path = 'build/' + url_path
    return f"https://docs.near.org/docs/{url_path}/{id}"

def replace_github_with_code(content: str) -> str:
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

def get_content_and_summary(document: str) -> str:
    # remove all `import ...` and iframes
    document = re.sub(r"import .*?\n", "", document)
    document = re.sub(r'<iframe.*?</iframe>', '', document, flags=re.DOTALL)

    # Our summaries are always in the second section delimited by ---
    groups = document.split("---")
    summary = document
    if groups: summary = groups[2]

    # the rest is the content
    content = document.replace(summary, "")
    content = content.replace("".join(groups[0:2]), "").replace("------\n\n", "")
    content = content if content else summary
    content = replace_github_with_code(content)

    # remove HTML tags leaving only the text
    summary = re.sub(r'<iframe.*?</iframe>', '', summary, flags=re.DOTALL)
    summary = re.sub(r'<.*?>', '', summary)

    # remove ' from the summary, so Let's becomes Lets
    summary = re.sub(r'\'(.)', r'\1', summary)

    # Encode the summary to avoid issues with the API
    summary = summary.encode().decode('unicode_escape')

    return content, summary

# ---------------- Load NEAR AI Hub configuration
CONFIG = Config()
config_data = load_config_file(local=False)
CONFIG = CONFIG.update_with(config_data)
base_url = CONFIG.api_url + "/v1"
client_config = ClientConfig(base_url=base_url, auth=CONFIG.auth)
client = openai.OpenAI(base_url=base_url, api_key=json.dumps(config_data["auth"]))

# Upload and attach add files to the vector store, skip existing vector-store doc file
map2map = {
    'tools': 'tools',
    'web3-apps': 'integration',
    'chain-abstraction': 'abstraction',
    'data-infrastructure': 'infrastructure',
    'primitives': 'primitives',
    'concepts': 'concepts',
    'smart-contracts': 'contracts'
}

category2vs = {}
id2meta = {}

categories = [dir for dir in glob("*") if os.path.isdir(dir)]

for c in categories:

    # Create a vector store for vector store docs
    md_files = [file for file in glob(f"./{c}/**/*.md", recursive=True)]

    docs_urls = []
    local_files = []
    summaries = []

    for file_path in md_files:
        print(f"Processing {c} {os.path.basename(file_path)}")
        with open(file_path, 'r') as file:
            content = file.read()
            clean_content, summary = get_content_and_summary(content)
            docs_url = derive_url(file_path, content)

            # Dump the clean content into a local file
            os.makedirs(f"../1.0.0/knowledge/{os.path.dirname(file_path[2:])}", exist_ok=True)
            with open(f"../1.0.0/knowledge/{file_path[2:]}", 'w') as f:
                f.write(clean_content)

            summaries.append(f"{prefix}{summary}")
            docs_urls.append(docs_url)
            local_files.append(f"./knowledge/{file_path[2:]}")

    try:
        embeddings = client.embeddings.create(
            input = summaries,
            model = embeddings_model
        )
        print(len(embeddings.data[0].embedding))
    except Exception as e:
        import ipdb; ipdb.set_trace()
        print(f"Error: {e}")
        embeddings = None

    df = pd.DataFrame.from_dict({
        "docs_url": docs_urls,
        "local": local_files,
        "embeddings": [e.embedding for e in embeddings.data]
    })

    df.to_csv(f"{c}.csv", index=False)

    # move document to ../1.0.0
    os.rename(f"{c}.csv", f"../1.0.0/{c}.csv")