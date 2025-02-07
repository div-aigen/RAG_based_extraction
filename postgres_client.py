import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Client(object):
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __del__(self):
        self.connection.close()

    def set_connection(self, host, port, database, user, password):
        """sets up the connection to postgres"""
        self.connection = psycopg2.connect("host=%s port=%s user=%s password=%s dbname=%s"
                                           %(host, port, user, password, database))

    def next_val(self, key, schema="public"):
        """gives the value of the next id sequence"""
        return self.fetch_one("select nextval(%s);", (f"{schema}.{key}",))[0]

    def fetch_one(self, cmd, var):
        """returns one result from cmd"""
        with self.connection.cursor() as cursor:
            try:
                if var is None:
                    cursor.execute(cmd)
                else:
                    cursor.execute(cmd, var)
                result = cursor.fetchone()
                self.connection.commit()
            except psycopg2.ProgrammingError as e:
                logger.error(f"cmd {cmd} failed due to {e}")
                self.connection.commit()
                result = False
        return result

    def fetch_all(self, cmd, var):
        """returns all the results for a query"""
        with self.connection.cursor() as cursor:
            try:
                if var is None:
                    cursor.execute(cmd)
                else:
                    cursor.execute(cmd, var)
                result = cursor.fetchall()
                self.connection.commit()
            except psycopg2.ProgrammingError as e:
                logger.error(f"cmd {cmd} failed due to {e}")
                self.connection.commit()
                result = []
        return result

    def execute(self, cmd, var):
        """executes a command, returns true if successful"""
        with self.connection.cursor() as cursor:
            try:
                if var is None:
                    cursor.execute(cmd)
                else:
                    cursor.execute(cmd, var)
                result = True
                self.connection.commit()
            except psycopg2.ProgrammingError as e:
                logger.error(f"cmd {cmd} failed due to {e}")
                self.connection.commit()
                result = []
        return result

    def create_embeddings_table(self, dim):
        """creates a table with a vector column for storing embeddings
            dim: The number of dimensions the embedding model operates on
        """
        create_extension_cmd = "create extension if not exists vector;"
        create_table_cmd = f"""
            create table if not exists sentence_embeddings (
                id serial primary key,
                sentence text,
                embedding vector({dim})
            );
        """
        self.execute(create_extension_cmd, None)
        self.execute(create_table_cmd, None)

    def insert_embeddings(self, sentences, embeddings):
        """insert each sentence and its embedding into the database"""
        for sentence, embedding in zip(sentences, embeddings):
            embedding_list = embedding.tolist()
            # check for duplicates
            fetch_cmd = f"""
                select 
                    sentence 
                from sentence_embeddings
                where
                    sentence = '{sentence}'
            """
            dup_data = self.fetch_one(fetch_cmd, None)
            if dup_data is None:
                insert_cmd = """
                    insert into sentence_embeddings (sentence, embedding)
                    values (%s, %s);
                """
                self.execute(insert_cmd, (sentence, embedding_list))
                logger.info(f"The sentence '{sentence}' has been added with the embedding")
            else:
                logger.info(f"The sentence '{sentence}' is already embedded and stored in the DB")
        return None
