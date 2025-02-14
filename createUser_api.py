from fastapi import FastAPI, status
import logging
import postgres_client
from create_user import create_user, delete_user
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

app = FastAPI(title="User Sign Up")

@app.post("/signup")
def user_sign_up(username: str, password: str):
    creation = create_user(username, password, client)
    if creation:
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User created successfully"
        }
    else:
        return {
            "status": status.HTTP_409_CONFLICT,
            "message": "Username already taken, choose another..."
        }

@app.post("/deleteUser")
def remove_user(username: str):
    deletion = delete_user(username, client)
    if deletion:
        return {
            "status": status.HTTP_200_OK,
            "message": "User deleted successfully"
        }
    else:
        return {
            "status": status.HTTP_409_CONFLICT,
            "message": "Error in deleting the user from DB."
        }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
