# BUILD VECTOR STORE FROM FILES
import json
import os
import re

from glob import glob
from urllib.parse import urlparse

import openai
import pandas as pd
import requests
import nearai


def replace_github_with_code(content: str) -> str:
    githubs = re.findall(r"<Github\s[^>]*?/>", content)
    formatted = content
    for gh in githubs:
        gh = gh.replace("'", '"')
        url = re.search(r'url="(.*?)"', gh).group(1)

        (url, *_) = url.split("#")
        (org, repo, _, branch, *pathSeg) = urlparse(url).path[1:].split("/")
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


def clean_content(content: str) -> str:
    # remove all `import ...`
    content = re.sub(r"import .*?\n", "", content)

    # Markdown has metadata at the beginning that we don't need
    groups = content.split("---")
    content = content.replace(groups[1], "").replace("------\n\n", "")

    # Load all the code blocks from Github
    content = replace_github_with_code(content)

    # Temporarily replace code blocks with placeholders
    code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
    placeholders = [f"__CODE_BLOCK_{i}__" for i in range(len(code_blocks))]

    for i, block in enumerate(code_blocks):
        content = content.replace(block, placeholders[i])

    # remove HTML tags leaving only the text
    content = re.sub(r'<iframe.*?</iframe>', '', content, flags=re.DOTALL)
    content = re.sub(r'<.*?>', '', content)

    # remove ' from the summary, so Let's becomes Lets
    content = re.sub(r'\'(.)', r'\1', content)

    # Encode the summary to avoid issues with the API
    try:
        content = content.encode().decode('unicode_escape')
    except UnicodeDecodeError:
        pass

    return content


# Load NEAR AI Hub configuration
config = nearai.config.load_config_file()
base_url = config.get("api_url", "https://api.near.ai/") + "v1"
auth = config["auth"]

client = openai.OpenAI(base_url=base_url, api_key=json.dumps(auth))

# Create embeddings for all files
embeddings_model = "fireworks::nomic-ai/nomic-embed-text-v1.5"
prefix = "classification: "

docs = []
md_files = list(glob("./**/*.md", recursive=True))

for file_path in md_files:
    print(f"Processing {file_path}")

    with open(file_path, 'r') as file:
        content = file.read()
        processed_doc = clean_content(content)

        docs.append(f"{prefix}{processed_doc}")

embeddings = client.embeddings.create(
    input=docs,
    model=embeddings_model
)

df = pd.DataFrame.from_dict({
    "docs": docs,
    "embeddings": [e.embedding for e in embeddings.data]
})

df.to_csv("embeddings.csv", index=False)
