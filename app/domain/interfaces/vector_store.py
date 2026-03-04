from abc import ABC, abstractmethod

from app.domain.entities.document import Document


class VectorStore(ABC):
    @abstractmethod
    def add(self, document: Document) -> None:
        pass

    @abstractmethod
    def search(self, query: str, top_k: int) -> list[Document]:
        pass