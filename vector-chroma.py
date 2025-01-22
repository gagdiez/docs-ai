# BUILD VECTOR STORE FROM FILES
import json
import openai
import os
import time

from glob import glob

from nearai.shared.client_config import ClientConfig
from nearai.shared.inference_client import InferenceClient, AutoFileChunkingStrategyParam
from nearai.config import Config, load_config_file

import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="my_collection")
# ---------------- Load NEAR AI Hub configuration

# Upload and attach add files to the vector store, skip existing vector-store doc file
md_files = [file  for file in glob("./dataset/concepts/**/*.md", recursive=True)]

# Create a vector store for vector store docs
for file_path in md_files:
    print(f"Processing {os.path.basename(file_path)}")

    with open(file_path, 'r') as file:
        collection.add(
            documents=[file.read()],
            ids=[file_path]
        )

# Poll the vector store status until processing is complete
import ipdb; ipdb.set_trace()

results = collection.query(
    query_texts=["What is a smart contract?"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)

# inference = InferenceClient(client_config)
# search_query = "What is a smart contract?"
# vector_results = inference.query_vector_store(vs.id, search_query)

print("end")

# def process_vector_results(results) -> List[Dict[str, Any]]:
#     flattened_results = [item for sublist in results for item in sublist]
#     # print("flattened_results", flattened_results)
#     return flattened_results[:20]


# def generate_llm_response(messages, processed_results):
#     system_prompt = """
#     You're an AI assistant that writes technical documentation. You can search a vector store for information relevant
#     to the user's query.
#     Use the provided vector store results to inform your response, but don't mention the vector store directly.
#     """

#     model = "qwen2p5-72b-instruct"

#     vs_results = "\n=========\n".join(
#         [f"{result.get('chunk_text', 'No text available')}" for result in processed_results]
#     )
#     messages = [
#         {"role": "system", "content": system_prompt},
#         *messages,
#         {
#             "role": "system",
#             "content": f"User query: {messages[-1]['content']}\n\nRelevant information:\n{vs_results}",
#         },
#     ]
#     return inference.completions(model=model, messages=messages, max_tokens=16000)


# # Retrieve the vector store details
# retrieved_store = client.beta.vector_stores.retrieve(vs_id)
# print(f"Vector Store details: {retrieved_store}")

# # Let's run a LLM completions using vector store we just created
# search_query = """Create markdown documentation for the new NearAI feature: Vector Stores. Provide a general
# explanation of what Vector Stores are and how they function.
# - Explain how to create a Vector Store, including uploading files, retrieving them, and deleting them.
# - Describe how to search within the Vector Store.
# - Explain how to obtain LLM responses using the Vector Store.

# Always include Python examples with comments. Ensure that all necessary functions used in the examples are included.
# Please generalize the examples."""

# inference = InferenceClient(client_config)
# vector_results = inference.query_vector_store(vs_id, search_query)
# processed_results = process_vector_results([vector_results])
# # Create chat history for LLM
# messages = [{"role": "user", "content": search_query}]
# llm_response = generate_llm_response(messages, processed_results)
# response_message = llm_response["choices"][0]["message"]["content"]

# print(response_message)

# # with open("doc.md", 'w') as file:
# #     file.write(response_message)