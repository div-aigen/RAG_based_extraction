import postgres_client
import os
from typing import List, Any, Optional
from input_query import UserInput

client = postgres_client.Client()
client.set_connection(
    os.getenv("host"),
    os.getenv("port"),
    os.getenv("dbname"),
    os.getenv("username"),
    os.getenv("password")
)

MODELNAME = "all-MiniLM-L6-v2"

def fetch_user_embedding(dbclient: Any) -> Optional[List]:
    user_client = UserInput(MODELNAME, client)
    user_input = input("How can I help you?: ")
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

def find_similar_sentence(dbclient: Any, query_embedding: List, n=5):
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

if __name__ == "__main__":
    embed = fetch_user_embedding(client)
    similar = find_similar_sentence(client, embed)
    print("This might be of help: ", similar)
