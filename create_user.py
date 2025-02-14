import postgres_client
from auth import pwd_context
import logging

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_user(username: str, password: str, db_client: postgres_client.Client):
    """Create a new user in the database"""
    hashed_password = pwd_context.hash(password)
    query_insert = """
        insert into user_data (username, hashed_password)
        values (%s, %s)
        returning username;
    """
    query_check = """
        select username
        from user_data
        where username = %s
    """
    check = db_client.fetch_one(query_check, (username,))
    if check:
        print("User already exists in the database.")
        return None
    else:
        try:
            result = db_client.execute(query_insert, (username, hashed_password))
            print(f"User added successfully: {result}")
            return result is not None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False


def delete_user(username: str, db_client: postgres_client.Client):
    """Properly delete a user and clean up constraints"""
    queries = [
        # Delete the user
        "delete from user_data where username = %s;",
        # Reset the sequence if needed
        "select setval('user_data_id_seq', coalesce((select max(id) from user_data), 1), false);"
    ]

    try:
        for query in queries:
            db_client.execute(query, (username,) if '%s' in query else None)
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False