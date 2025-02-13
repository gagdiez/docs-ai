from nearai.shared.client_config import ClientConfig
from nearai.config import Config, load_config_file
import openai
import json
from nearai.shared.inference_client import InferenceClient

CONFIG = Config()
config_data = load_config_file(local=False)
CONFIG = CONFIG.update_with(config_data)
base_url = CONFIG.api_url + "/v1"
client_config = ClientConfig(base_url=base_url, auth=CONFIG.auth)
client = openai.OpenAI(base_url=base_url, api_key=json.dumps(config_data["auth"]))

user_query = "How can I add an access key to my account?"
embedding_model = "fireworks::nomic-ai/nomic-embed-text-v1.5"
vector_stores = json.load(open("category_vector_store.json"))
vector_metadata = json.load(open("vector_metadata.json"))

inference = InferenceClient(client_config)
vector_results = inference.query_vector_store(vector_stores['tools'], user_query)

for res in vector_results:
    url = vector_metadata[res['file_id']]['docs_url']
    distance = res['distance']
    print(url, distance)