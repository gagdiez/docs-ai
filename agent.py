import json

from typing import List, Dict, Any
from nearai.shared.client_config import ClientConfig
from nearai.shared.inference_client import InferenceClient
from nearai.config import Config, load_config_file
from nearai.agents.environment import Environment

MODEL="llama-v3p1-70b-instruct"
TAG2VID = json.load(open("tags2vid.json"))
ID2URL = json.load(open("id2url.json"))

tags = list(TAG2VID.keys())


def run(env: Environment):
    # Your agent code here
    router_prompt = {
        "role": "system",
        "content": f"""
                    I am a router that helps users find the right expert to answer their questions about NEAR.

                    Here is what experts specialize in:

                    abstraction: Meta Transactions and Relayers (covering users' transaction fees), and other chains like Ethereum or Bitcoin.
                    primitives: Fungible tokens (FT), non-fungible tokens (NFT), linkdrops, oracles, Decentralized Autonomous Organizations (DAOs), and Decentralized Exchanges (DEXs).
                    contracts: Creating, testing, and deploying generic smart contracts on NEAR.
                    integration: Creating frontend and backend applications that interact with NEAR.
                    infrastructure: Using Indexers and BigQuery for analyzing NEAR data.
                    tools: How to use Wallets, APIs and CLIs to add keys, create accounts, delete accounts, call methods on contracts, deploy contracts, and transfer tokens.
                    concepts: NEAR's core concepts such as Accounts, Access Keys, Transactions, and Gas.

                    I will respond with a single tag from this list: [{[f"{tag}" for tag in tags]}]

                    For conceptual or theoretical queries (e.g., 'what is X'), I prioritize the "concepts" tag. Otherwise, I match the user with the most relevant tag.
                    """
    }

    tag = env.completion([router_prompt] + env.list_messages(), model=MODEL)

    # Check if the LLM has returned a (semi)valid tag
    if any((t in tag.lower() for t in tags)):
        expert = [t for t in tags if t in tag.lower()][0]
        print(f"Asking an expert on {tag}")
        expert_answer(env, user_query=env.list_messages()[-1]["content"], expert=expert)
    else:
        env.add_reply(f"I'm not sure what you mean, can you ask again?")
        return

# EXPERTS
expert_context = {
    "tools": """
    The agent has access to the documentation of:
        - near-cli: Handles accounts, keys, tokens, contracts, and more from the terminal
        - near-api: Handles accounts, keys, tokens, contracts, and more from Javascript, Rust and Python applications
        - near-wallet: Information on the different wallets that are available on NEAR
        - near-wallet-selector: A javascript library that helps users connect their wallets in a frontend
        - near-explorer: A web-based tool to query the transaction history
        - ethereum-wallets: How to use Ethereum wallets to interact with NEAR
        - data-apis: Libraries to access transaction history from a frontend or backend
    
    The agent will respond with a vector of tags from the list above. Always provide a valid and well-structured JSON response. No additional text is allowed outside the JSON vector
    """,
    "generic": """
    Answer using a JSON object:

    {
        "answer": a concise answer to the user, using as few chunks as possible and staying as close as possible to the Official NEAR Docs,
        "ids": The IDs of the documents used to generate the answer}'
    }

    Always provide a valid and well-structured JSON response. No additional text is allowed outside the JSON format
"""
}

def keep_k_best(results, k=3) -> List[Dict[str, Any]]:
    # order by 'distance' and keep the top k
    results.sort(key=lambda x: x["distance"])
    return [{"file_id": r["file_id"], "file_content": r["chunk_text"]} for r in results[:k]]

def expert_answer(env: Environment, user_query: str, expert: str):
    # import ipdb; ipdb.set_trace()

    # Get all the possible contexts
    # context_prompt = expert_context[expert] if expert in expert_context.keys() else expert_context["generic"]

    # contexts = ["near"]
    # try:
    #     contexts = json.loads(env.completion([{"role": "user", "content": user_query}, {"role": "system", "content": context_prompt}], model=MODEL))
    # except:
    #     pass
    
    # # Retrieve the vector store
    # CONFIG = Config()
    # CONFIG = CONFIG.update_with(load_config_file(local=False))
    # client_config = ClientConfig(base_url=CONFIG.api_url + "/v1", auth=CONFIG.auth)
    # inference = InferenceClient(client_config)

    # vector_results = []
    # for cntx in contexts:
    #     vector_results += inference.query_vector_store(TAG2VID[expert], f"{cntx}: {user_query}", full_files=True)
        
    # Retrieve the vector store
    CONFIG = Config()
    CONFIG = CONFIG.update_with(load_config_file(local=False))
    client_config = ClientConfig(base_url=CONFIG.api_url + "/v1", auth=CONFIG.auth)
    inference = InferenceClient(client_config)
    import ipdb; ipdb.set_trace()

    vector_results = inference.query_vector_store(TAG2VID[expert], user_query, full_files=False)
    processed_results = keep_k_best(vector_results, 10)
    messages = [
        {
            "role": "user",
            "content": f"{user_query}.",
        },
        {
            "role": "Official NEAR Docs",
            "content": json.dumps(processed_results),
        },
        {
            "role": "system",
            "content": "Answer using just a JSON Vector with the most relevant file_ids from the Official NEAR Docs.",
        },
    ]

    results = env.completion(model=MODEL, messages=messages)
    
    response = json.loads(results)
    response = list(set(response))

    env.add_reply('<ul>' + ''.join([f"<ui> <a href='{ID2URL[id]}'>{ID2URL[id]}</a> </ui>" for id in response]) + '</ul>')

    # env.add_reply(f"""{response["answer"]}

    # For more information, check: 
    # <ul>{''.join([f"<ui> <a href='{ID2URL[id]}'>{ID2URL[id]}</a> </ui>" for id in response["ids"]])}</ul>""")

run(env)