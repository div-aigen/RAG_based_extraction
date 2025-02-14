from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
import logging
import main
import postgres_client
import os
import uvicorn
from auth import create_access_token, verify_token, get_user_from_db, verify_password
from datetime import timedelta

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

api = FastAPI(title="Retrieval Chat")

@api.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    user = get_user_from_db(form_data.username, client)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api.post("/chat/{user_query}")
async def fetch(user_query: str, current_user: str = Depends(verify_token)):
    """Protected chat endpoint"""
    embed = main.fetch_user_embedding(client, user_query)
    similar_results = main.find_similar_sentence(client, embed)
    context = main.format_context(similar_results)
    response = main.generate_response(user_query, context)
    return {
        "user_input": user_query,
        "Response": response
    }

@api.get("/health")
def health_check():
    """Health check endpont"""
    return {"status": "healthy"}

if __name__ == '__main__':
    uvicorn.run(api, host="0.0.0.0", port=8800)
