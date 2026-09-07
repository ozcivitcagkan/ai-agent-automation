import chromadb

client_db = chromadb.PersistentClient(path="./chroma_db")
koleksiyon = client_db.get_or_create_collection(name="sirket_politikalari")

print(koleksiyon.count())
print(koleksiyon.get(ids=["chunk_0"]))