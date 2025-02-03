import json
import chromadb

from typing import Dict, List
from nearai.agents.environment import Environment

MODEL="llama-v3p3-70b-instruct"

client = chromadb.PersistentClient(path=f".")

tags = ["tools", "integration", "abstraction", "infrastructure", "primitives", "concepts", "contracts"]

def run(env: Environment):
    router_prompt = {
        "role": "system",
        "content": f'''
                    I am a router that helps users find the right expert to answer their questions about NEAR.

                    Here is what each expert specializes in:

                    abstraction: Meta Transactions and Relayers (covering users' transaction fees), and other chains like Ethereum or Bitcoin.
                    primitives: Fungible tokens (FT), non-fungible tokens (NFT), linkdrops, oracles, Decentralized Autonomous Organizations (DAOs), and Decentralized Exchanges (DEXs).
                    contracts: Creating, testing, and deploying generic smart contracts on NEAR.
                    integration: Creating frontend and backend applications that interact with NEAR.
                    infrastructure: Using Indexers and BigQuery for analyzing NEAR data.
                    tools: How to use Wallets, APIs and CLIs to add keys, create accounts, delete accounts, call methods on contracts, deploy contracts, and transfer tokens.
                    concepts: NEAR's core concepts such as Accounts, Access Keys, Transactions, and Gas.

                    I will respond with a valid strict JSON dictionary:
                    
                    {{
                      "expert": "a single str from this list: [{[f'{tag}' for tag in tags]}, 'unknown']",
                      "query": "repeat the very last user query, note that some queries might span multiple messages"
                    }}

                    I will add nothing else before or after the JSON dictionary.
                    '''
    }

    # keep only the user messages to save tokens
    messages = [m for m in env.list_messages() if m["role"] == "user"]
    response = env.completion(messages + [router_prompt], model=MODEL)

    try:
        response = json.loads(response)
        expert = response["expert"]
        query = response["query"]

        # Check if the LLM has returned a (semi)valid tag
        if not any((t in expert.lower() for t in tags)):
            return env.add_reply(f"I'm not sure what you mean, can you ask again?")

        expert = [t for t in tags if t in expert.lower()][0]
        env.add_reply(f"Asking an expert on {expert}")
        
        docs_ids = expert_find_docs(env, user_query=query, expert=expert)
        env.add_reply(f"Found some relevant pages: {', '.join(docs_ids)}. Let me try to summarize them for you.")

        summary = expert_answer(env, user_query=query, expert=expert, docs_ids=docs_ids)
        env.add_reply(summary)
    except:
        env.add_message('user', )
        env.add_reply(f"I'm not sure what you mean, can you ask again?")

def expert_find_docs(env: Environment, user_query: str, expert: str):
    vector_store = client.get_collection(expert)

    # Search the vector store for the most relevant documents
    vector_results = vector_store.query(query_texts=user_query, n_results=3)
    ids, documents = vector_results["ids"], vector_results["documents"]
    processed_results = [{"id": ids[i], "summary": documents[i]} for i in range(len(ids))]
    import ipdb; ipdb.set_trace()
    # Generate a response
    messages = [
        {
            "role": "user query",
            "content": user_query,
        },
        {
            "role": "official NEAR docs",
            "content": json.dumps(processed_results),
        },
        {
            "role": "system",
            "content": "A strict and valid JSON vector containing only the id of the most relevant documents that can answer the user's query.",
        },
    ]

    results = env.completion(model=MODEL, messages=messages)
    response = json.loads(results)
    response = list(set(response))
    return response

def expert_answer(env: Environment, user_query: str, expert: str, docs_ids: List[str]):
    vector_store = client.get_collection(expert)

    # Get the full content of the documents
    full_docs = [meta['full_content'] for meta in vector_store.get(ids=docs_ids)['metadatas']]
    processed_results = [{"id": docs_ids[i], "full_text": full_docs[i]} for i in range(len(docs_ids))]

    # Generate an answer
    messages = [
        {
            "role": "user query",
            "content": user_query
        },
        {
            "role": "official NEAR docs",
            "content": json.dumps(processed_results),
        },
        {
            "role": "system",
            "content": "I will answer the user's query in a concise way, staying as close and true as possible to the official documentation."
        },
    ]

    return env.completion(model=MODEL, messages=messages)

run(env)
    