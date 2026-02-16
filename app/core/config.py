import os


class LLMConfig:
    path = os.getenv("MODEL_PATH", "models/gemma-2-9b-it-abliterated-Q3_K_M.gguf")
    gpu_layers = 20
    max_context = 2048
    completion_temp = 0.4
    summarization_temp = 0.2
