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
- Add a users table in the database which stores the usernames and hashed passwords. (Implemented)
- Add an authorization method which verifies the access token from the user in order to allow chat access. (Implemented)
- Each new document can be inconvenient to store in the same database. But storing in separate DBs might cause scaling problems. 
Optimally, store new documents in new schemas within the same DB:
  - define a new schema parameter in the methods
  - the schema name can be the name of the document (default=public)
  - the naming convention for the embeddings table should be {schemaname}_embeddings (for convenience)
  - There should be a separate api which can add the knowledge documents to the specific schema and table.