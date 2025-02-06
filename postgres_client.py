from logging import DEBUG
import psycopg2
import logging

logging.basicConfig(level=DEBUG)
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
