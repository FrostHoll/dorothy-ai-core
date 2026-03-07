import time

from llama_cpp import Llama

from app.core.config import LLMConfig as Config
from app.domain.entities.message import Message

class LlamaEngine:
    def __init__(self):
        self.model = Llama(
            model_path = Config.path,
            n_ctx = Config.max_context,
            verbose = False
        )
        self.generated_text = ""
        print("[LLM]: LLama Engine initialized.")

    def _create_chat_completion(self, prompt):
        stream = self.model.create_chat_completion(
            messages=prompt,
            temperature=Config.completion_temp,
            stream=True
        )

        for chunk in stream:
            if "content" in chunk["choices"][0]["delta"]:
                token = chunk["choices"][0]["delta"]["content"]
            else:
                token = ""
            self.generated_text += token
            yield token

    def create_chat_completion(self, prompt) -> tuple[Message, str, int]:
        self.generated_text = ""
        total_tokens_generated = 0
        prompt_tokens = 0
        for i in prompt:
            prompt_tokens += len(self.model.tokenize(text = i["content"].encode("utf-8")))
        start_time = time.time()
        for token in self._create_chat_completion(prompt):
            if token.strip():
                total_tokens_generated += 1

        end_time = time.time()
        total_tokens = total_tokens_generated + prompt_tokens
        text = self.generated_text.strip()
        print(f"[LLM]: Prompt tokens: {prompt_tokens} Generated tokens: {total_tokens_generated} Total: {total_tokens}/{Config.max_context}")
        print(f"[LLM]: Response:({text}) Generation time: {end_time - start_time:.2f} s")
        return Message(role="assistant", content=text, token_count=total_tokens_generated), self.generated_text, total_tokens

##TODO: complete restore and summarization logic

    def create_restore_completion(self, prompt):
        pass

    def create_summarization_completion(self, prompt):
        pass

    def count_tokens(self, text: str) -> int:
        return len(self.model.tokenize(text=text.encode("utf-8")))