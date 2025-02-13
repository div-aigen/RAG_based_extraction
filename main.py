import postgres_client
import os
from typing import List, Any, Optional
from input_query import UserInput
from groq import Groq

client = postgres_client.Client()
client.set_connection(
    os.getenv("host"),
    os.getenv("port"),
    os.getenv("dbname"),
    os.getenv("username"),
    os.getenv("password")
)

groq_client = Groq(api_key=os.getenv("groq_api_key"))
MODELNAME = "all-MiniLM-L6-v2"

def fetch_user_embedding(dbclient: Any, user_input: str) -> tuple[Optional[List], str]:
    user_client = UserInput(MODELNAME, client)
    user_client.get_input_embeddings(user_input)
    cmd = f"""
        select 
            input_embedding
        from user_query
        where
            user_input = '{user_input}'
    """
    embedding_user = dbclient.fetch_one(cmd, None)
    embedding = eval(embedding_user[0])
    return embedding

def find_similar_sentence(dbclient: Any, query_embedding: tuple[Optional[List], str], n=5):
    """makes a similarity search to the knowledge base in the database"""
    query_cmd = """
        select 
            sentence, 
            embedding <-> %s::vector as distance
        from sentence_embeddings
        order by distance asc
        limit %s;
    """
    return dbclient.fetch_all(query_cmd, (query_embedding, n))

def format_context(similar_results: List) -> str:
    """Format all the similar sentences into a context string"""
    context = "\n".join([result[0] for result in similar_results])
    return context

def generate_response(user_query: str, context: str, chat_model="llama3-8b-8192") -> str:
    """Generate a chat response using a model (Using Groq due to no GPU)"""
    system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
    Use the context to provide accurate and relevant answers. If the context doesn't contain 
    enough information to answer the question fully, acknowledge this and stick to what can be 
    answered from the context. Just start with the response directly. Also, avoid copying words as it 
    is from the document."""

    prompt = f"""Context: {context}\n\nQuestion: {user_query}\n\nPlease answer the question based on the 
            context provided."""

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=chat_model,
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    user_ask = input("How can I help you?: ")
    embed = fetch_user_embedding(client, user_ask)
    similar_results_ = find_similar_sentence(client, embed)
    context_ = format_context(similar_results_)
    response = generate_response(user_ask, context_)
    print("\nResponse: ", response)
