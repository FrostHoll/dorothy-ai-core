from abc import ABC, abstractmethod

class EmbeddingInterface(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass