import json

import openai
import nearai
import numpy as np
import pandas as pd
from nearai.agents.environment import Environment

# Load NEAR AI Hub configuration
config = nearai.config.load_config_file()
base_url = config.get("api_url", "https://api.near.ai/") + "v1"
auth = config["auth"]

client = openai.OpenAI(base_url=base_url, api_key=json.dumps(auth))

MODEL = "llama-v3p3-70b-instruct"

df = pd.read_csv('./embeddings.csv')
EMBEDDING_MODEL = "fireworks::nomic-ai/nomic-embed-text-v1.5"
PREFIX = "classification: "


def cosine_similarity(a, b):
    a = np.matrix(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def run(env: Environment):
    user_query = env.list_messages()[-1]["content"]

    embedding = client.embeddings.create(
                input=[f"{PREFIX}{user_query}"],
                model=EMBEDDING_MODEL,
            ).data[0].embedding

    df['similarities'] = df.embeddings.apply(
        lambda x: cosine_similarity(x, embedding)
    )

    res = df.sort_values('similarities', ascending=False).head(6)

    prompt = [
        {
            "role": "user query",
            "content": user_query,
        },
        {
            "role": "documentation",
            "content": json.dumps(res.docs.tolist()),
        },
        {
            "role": "system",
            "content": "Give a brief but complete answer to the user's query, staying as true as possible to the documentation SPECIALLY when dealing with code."
        }
    ]

    answer = env.completion(model=MODEL, messages=prompt)
    env.add_reply(answer)


run(env)
