# Data Intensive AI Applications with `pgvector`
Instead of using traditional vector database, this repository tackles with setting up vector database in PostgreSQL itself, using extensions. 
### base work set-up
- generate embeddings:
    - A whole document can be embedded to generate vectors (Implemented with chunking)
    - All the generated vectors should be stored in the database with the chunked text (Implemented)
    - The data should be indexed for easy and fast fetching (reduce latency)
    - The user query must also be embedded (Immplemented)
- perform cosine similarity to get the best answer to the user query (Implemented)
- scale in order to provide any new knowledge document during runtime (if any)
- a chat model is introduced which can gather all the fetched similarities and combine them to frame one answer. (Implemented)
- Add a users table in the database which stores the usernames and hashed passwords.
- Add an authorization method which verifies the access token from the user in order to allow chat access.
