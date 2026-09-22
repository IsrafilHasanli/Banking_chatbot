from app.rag.rag import ingest_folder
from app.core.db.qdrant_db import client
if __name__ == "__main__":
    ingest_folder("./app/rag/pdfs/")

print(client.get_collections())
print(client.count(collection_name="bank_docs"))