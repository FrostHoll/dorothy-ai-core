from app.domain.entities.message import Message
from app.domain.interfaces.llm_interface import LLMInterface
from app.infrastructure.llm.lms_engine import LMSEngine
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_container import ToolContainer
from app.core.config import LLMConfig as Config


class LLMWithTools(LLMInterface):
    def __init__(self, llm_engine: LMSEngine, tool_container: ToolContainer):
        self.llm = llm_engine
        self.tool_container = tool_container

    async def create_chat_completion(self, messages: list[Message]) -> tuple[Message, str, int]:
        raise NotImplementedError("Cannot use completion without tools")

    async def create_chat_completion_with_tools(self, messages: list[Message]) -> tuple[list[Message], list[str], int]:
        tools_prompt = self.tool_container.get_tools_prompt()
        msg, text, predicted_tokens, tool_calls = await self.llm.create_chat_completion(messages, tools_prompt)


        if len(tool_calls) > 0:

            result_messages = [msg]
            temp_messages = [msg]
            texts = [text]
            result_tokens = 0
            while len(tool_calls) > 0:
                result_tokens += predicted_tokens
                print(tool_calls)

                for tool_call in tool_calls:
                    #call = f"<|tool_call>call:{tool_call["name"]}{{}}<tool_call|>"
                    texts.append(TextPostprocessor.get_display_text_by_tool_call(tool_call))
                    try:
                        result = await self.tool_container.execute(tool_call)
                        result = f"response:{tool_call["name"]}{{{result}}}"
                        print(result)

                        tool_call_tokens = self.count_tokens(result)
                        result_tokens += tool_call_tokens

                        tool_response_msg = Message(role="tool", content=result, token_count=tool_call_tokens)

                        temp_messages.append(tool_response_msg)
                        result_messages.append(tool_response_msg)
                    except Exception as e:
                        print(f"Tool execution failure: {str(e)}")

                        error_text = f"Failure during execution of tool {tool_call["name"]}: {str(e)}"

                        error_msg_tokens = self.count_tokens(error_text)
                        result_tokens += error_msg_tokens

                        err_message = Message(role="tool", content=error_text, token_count=error_msg_tokens)

                        temp_messages.append(err_message)
                        result_messages.append(err_message)

                messages.extend(temp_messages)
                temp_messages.clear()

                msg, text, predicted_tokens, tool_calls = await self.llm.create_chat_completion(messages, tools_prompt)

            result_messages.append(msg)
            texts.append(text)
            result_tokens += predicted_tokens
            return result_messages, texts, result_tokens
        else:
            return [msg], [text], predicted_tokens

    async def create_restore_completion(self, user_input: str):
        pass

    async def create_summarization_completion(self, user_input: str):
        pass

    def count_tokens(self, text: str) -> int:
        ## TODO: lamest thing i've ever done
        return len(text) // 3

    def get_context_window(self) -> int:
        return Config.max_context

    def get_reserved_tokens(self) -> int:
        return Config.reserved_tokens