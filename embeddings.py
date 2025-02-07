from logging import DEBUG
import postgres_client
from sentence_transformers import SentenceTransformer
import os
import logging
from chunking import sentence_chunking

logging.basicConfig(
    level=DEBUG
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


class GenerateEmbeddings:
    def __init__(self, modelname, dbclient):
        self.modelname = modelname
        self.client = dbclient

    def get_embeddings(self, file: str, max_tokens: int):
        """Load a pre-trained transformer model and calculate sentence embedding vectors
            Method parameters:
                file: This parameter represents a text file that would be chunked into segments
                max_tokens: This parameter is the maximum number of tokens that can exist within a chunk
        """
        model = SentenceTransformer(self.modelname)
        # sentences = [
        #     "Zinedine Zidane is a former football midfielder.",
        #     "He played for clubs like Real Madrid, and Juventus.",
        #     "He also won the 1998 World Cup with France."
        # ]
        with open(file, 'r', encoding='utf-8') as file:
            text = file.read()
        sentences = sentence_chunking(text, max_tokens)

        embeddings = model.encode(sentences)
        return sentences, embeddings


def main():
    embedder = GenerateEmbeddings(MODELNAME, client)
    sentences_, embeddings_ = embedder.get_embeddings('sample_text.txt', 20)
    client.create_embeddings_table(dim=embeddings_.shape[1])
    client.insert_embeddings(sentences_, embeddings_)
    client.connection.close()

if __name__ == "__main__":
    main()
