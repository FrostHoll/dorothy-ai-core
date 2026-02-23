from app.domain.entities.document import Document
from app.domain.interfaces.embedding_interface import EmbeddingInterface
from app.domain.interfaces.vector_store import VectorStore
from app.core.config import EmbeddingConfig as Config


import faiss
import numpy as np

class FAISSVectorStore(VectorStore):
    def __init__(self, embedding_service: EmbeddingInterface):
        self.index = faiss.IndexFlatIP(Config.embedding_dim)
        self.id_map = {}
        self.documents = {}
        self.embedding_service = embedding_service

    def add(self, document: Document) -> None:
        vector = self.embedding_service.embed(document.content)

        vector_np = np.array([vector]).astype("float32")

        self.index.add(vector_np)

        position = self.index.ntotal - 1

        self.id_map[position] = document.id

        self.documents[document.id] = document

    def search(self, query: str, top_k: int) -> list[Document]:
        query_vector = self.embedding_service.embed(query)
        query_np = np.array([query_vector]).astype("float32")

        scores, indices = self.index.search(query_np, top_k)

        results = []

        for idx in indices[0]:
            if idx == -1:
                continue

            doc_id = self.id_map.get(idx)
            if doc_id:
                results.append(self.documents[doc_id])

        return results