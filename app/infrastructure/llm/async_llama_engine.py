import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.llama_engine import LlamaEngine
from app.infrastructure.llm.llama_mapper import msg_list_to_llama_format
from app.core.config import LLMConfig as Config


class AsyncLLamaEngine(LLMInterface):
    def __init__(self):
        self.llm = LlamaEngine()
        self.loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers = 1)

    async def create_chat_completion(self, messages: list[Message]) -> tuple[Message, str, int]:
        prompt = msg_list_to_llama_format(messages)

        return await self.loop.run_in_executor(
            self.executor,
            self.llm.create_chat_completion,
            prompt
        )

    async def create_restore_completion(self, user_input: str):
        pass

    async def create_summarization_completion(self, user_input: str):
        pass

    ##TODO: complete restore and summarization logic

    def count_tokens(self, text: str) -> int:
        return self.llm.count_tokens(text)

    def get_context_window(self) -> int:
        return Config.max_context

    def get_reserved_tokens(self) -> int:
        return Config.reserved_tokens