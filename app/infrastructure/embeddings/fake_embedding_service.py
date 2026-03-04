from app.domain.interfaces.embedding_interface import EmbeddingInterface
from app.core.config import EmbeddingConfig as Config

import numpy as np
import hashlib


class FakeEmbeddingService(EmbeddingInterface):
    def embed(self, text: str) -> list[float]:
        words = text.lower().replace("\n", " ").split()
        vector = np.zeros(Config.embedding_dim, dtype=np.float32)

        for word in words:
            hash_digest = hashlib.sha256(word.encode('utf-8')).digest()

            idx = int.from_bytes(hash_digest[:4], 'little') % Config.embedding_dim
            val = int.from_bytes(hash_digest[4:8], 'little') % 100 / 100.0

            vector[idx] += val

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector