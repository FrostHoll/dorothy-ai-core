from app.domain.entities.document import Document
from app.domain.interfaces.embedding_interface import EmbeddingInterface
from app.domain.interfaces.vector_store import VectorStore
from app.infrastructure.embeddings.faiss_vector_store import FAISSVectorStore
from app.infrastructure.embeddings.fake_embedding_service import FakeEmbeddingService

if __name__ == "__main__":
    embedding_service: EmbeddingInterface = FakeEmbeddingService()
    store: VectorStore = FAISSVectorStore(embedding_service)

    store.add(Document(id="1", content="Я пишу игру про Фонд", metadata={}))
    store.add(Document(id="2", content="Сегодня идет дождь", metadata={}))
    store.add(Document(id="3", content="Мне нравится архитектура", metadata={}))

    results = store.search("нравится", top_k=2)

    for r in results:
        print(r.content)