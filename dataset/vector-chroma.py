import os
import re 
from glob import glob
from urllib.parse import urlparse

import chromadb
import requests

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
    # remove all `import ...`
    document = re.sub(r"import .*?\n", "", document)

    # Our summaries are always in the second section delimited by ---
    groups = re.search(r"---*.*?---*(.*?)\s*---", document, re.DOTALL)
    summary = document
    if groups: summary = groups.group(1)

    # the rest is the content
    content = document.replace(summary, "")
    content = content if content else summary

    content = replace_github_with_code(content)

    return content, summary


categories = [dir for dir in glob("*") if os.path.isdir(dir)]
client = chromadb.PersistentClient(path=f"./chroma/")

map2map = {
    'tools': 'tools',
    'web3-apps': 'integration',
    'chain-abstraction': 'abstraction',
    'data-infrastructure': 'infrastructure',
    'primitives': 'primitives',
    'concepts': 'concepts',
    'smart-contracts': 'contracts'
}

for c in categories:
    # Create a vector store for our docs
    collection = client.create_collection(name=map2map[c])

    md_files = [file for file in glob(f"./{c}/**/*.md", recursive=True)]

    for file_path in md_files:
        print(f"Processing {c} {os.path.basename(file_path)}")
        with open(file_path, 'r') as file:
            content = file.read()
            clean_content, summary = get_content_and_summary(content)
            file_id = derive_url(file_path, content)

            collection.add(
                documents=[summary],
                ids=[file_id],
                metadatas=[{"full_content": clean_content}]
            )