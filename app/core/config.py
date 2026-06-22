import os


class LLMConfig:
    ##TODO: Make model path variable depends on local/docker run
    #path = os.getenv("MODEL_PATH", "models/gemma-2-9b-it-abliterated-Q3_K_M.gguf")
    path = "C://Users//almaz//Downloads//Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    gpu_layers = 20
    max_context = 65536
    reserved_tokens = 2048
    completion_temp = 0.6
    summarization_temp = 0.2


class PersonaManagerConfig:
    directory = "personas//"
    persona_file = "persona.json"


class MemoryConfig:
    db_name = "memory.db"

class EmbeddingConfig:
    embedding_dim = 384