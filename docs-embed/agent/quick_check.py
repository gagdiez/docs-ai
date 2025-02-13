import pandas as pd
from nearai.shared.client_config import ClientConfig
from nearai.config import Config, load_config_file
import openai
import json
import numpy as np

CONFIG = Config()
config_data = load_config_file(local=False)
CONFIG = CONFIG.update_with(config_data)
base_url = CONFIG.api_url + "/v1"
client_config = ClientConfig(base_url=base_url, auth=CONFIG.auth)
client = openai.OpenAI(base_url=base_url, api_key=json.dumps(config_data["auth"]))

prefix = "classification: "

df = pd.read_csv('./tools.csv')
user_query = f"{prefix}How can I add an access key to my account?"
embedding_model = "fireworks::nomic-ai/nomic-embed-text-v1.5"

embedding = client.embeddings.create(
            input = [user_query],
            model=embedding_model,
        ).data[0].embedding

def cosine_similarity(a, b):
    a = np.matrix(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

df['similarities'] = df.embeddings.apply(lambda x: np.array(x)).apply(lambda x: cosine_similarity(x, embedding))
res = df.sort_values('similarities', ascending=False).head(9)
print(res)