import postgres_client
from sentence_transformers import SentenceTransformer
import os
import logging
from embeddings import GenerateEmbeddings

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

MODELNAME = "all-MiniLM-L6-v2"


class UserInput(GenerateEmbeddings):
    def __init__(self, modelname, dbclient):
        super().__init__(modelname, dbclient)

    def get_input_embeddings(self, sentence: str) -> None:
        """get the embeddings for the user query
            Method parameters:
                sentence: Since this is a user sentence, it will always be one at a time
        """
        model = SentenceTransformer(self.modelname)
        embedding = model.encode(sentence)
        self.client.insert_user_embeddings(sentence, embedding)
        return None
