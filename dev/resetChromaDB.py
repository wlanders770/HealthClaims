import chromadb
from chromadb.config import Settings
client = chromadb.PersistentClient(path="../chroma_data",settings=Settings(allow_reset=True))
client.reset()