import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.llama_engine import LlamaEngine
from app.infrastructure.llm.llama_mapper import msg_list_to_llama_format
from app.core.config import LLMConfig as Config
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_container import ToolContainer


class AsyncLLamaEngine(LLMInterface):
    def __init__(self, tool_container: ToolContainer | None = None):
        self.llm = LlamaEngine(tool_container)
        self.loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers = 1)
        self.tool_container = tool_container

    async def create_chat_completion(self, messages: list[Message]) -> tuple[Message, str, int]:
        prompt = msg_list_to_llama_format(messages)

        return await self.loop.run_in_executor(
            self.executor,
            self.llm.create_chat_completion,
            prompt
        )

    async def create_chat_completion_with_tools(self, messages: list[Message]) -> tuple[list[Message], list[str], int]:
        prompt = msg_list_to_llama_format(messages)

        message, text, total_tokens = await self.loop.run_in_executor(
            self.executor,
            self.llm.create_chat_completion,
            prompt
        )

        if "tool_call" in text:
            result_messages = [message]
            temp_messages = [message]
            texts = []
            result_tokens = 0

            while "tool_call" in text:
                clean_text, tool_calls = TextPostprocessor.process_tool_calls(text)

                texts.append(clean_text)
                result_tokens += total_tokens

                print(tool_calls)

                for tool_call in tool_calls:
                    try:
                        result = await self.tool_container.execute(tool_call)

                        result = f"response:{tool_call["name"]}{{{result}}}"
                        print(result)

                        tool_call_tokens = self.count_tokens(result)
                        result_tokens += tool_call_tokens

                        tool_response_msg = Message(role="assistant", content=result, token_count=tool_call_tokens)

                        temp_messages.append(tool_response_msg)
                        result_messages.append(tool_response_msg)
                    except Exception as e:
                        print(f"Tool execution failure: {str(e)}")

                        error_text = f"Failure during execution of tool {tool_call["name"]}: {str(e)}"

                        error_msg_tokens = self.llm.count_tokens(error_text)
                        result_tokens += error_msg_tokens

                        err_message = Message(role="assistant", content=error_text, token_count=error_msg_tokens)

                        temp_messages.append(err_message)
                        result_messages.append(err_message)

                messages.extend(temp_messages)
                temp_messages.clear()

                prompt = msg_list_to_llama_format(messages)

                message, text, total_tokens = await self.loop.run_in_executor(
                    self.executor,
                    self.llm.create_chat_completion,
                    prompt
                )

            result_messages.append(message)
            texts.append(text)
            result_tokens += total_tokens
            return result_messages, texts, result_tokens
        else:
            return [message], [text], total_tokens

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