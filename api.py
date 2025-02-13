from fastapi import FastAPI, HTTPException
import logging
import main
import postgres_client
import os
import uvicorn

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = postgres_client.Client()
client.set_connection(
    os.getenv("host"),
    os.getenv("port"),
    os.getenv("dbname"),
    os.getenv("username"),
    os.getenv("password")
)

api = FastAPI(title="Skibidi Chat")

@api.post("/chat/{user_query}")
def fetch(user_query: str):
    embed = main.fetch_user_embedding(client, user_query)
    similar_results = main.find_similar_sentence(client, embed)
    context = main.format_context(similar_results)
    response = main.generate_response(user_query, context)
    return {
        "user_input": user_query,
        "Response": response
    }

@api.get("/health")
async def health_check():
    """Health check endpont"""
    return {"status": "healthy"}

if __name__ == '__main__':
    uvicorn.run(api, host="0.0.0.0", port=8800)
