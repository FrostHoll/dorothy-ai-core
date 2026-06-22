import httpx
from app.domain.entities.message import Message
from app.infrastructure.llm.llama_mapper import msg_list_to_llama_format, llama_format_to_msg
import json
import time


class LMSEngine:
    def __init__(self):
        self.base_url = "http://localhost:1234/v1/chat/completions"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=240.0,
            follow_redirects=True
        )

    async def create_chat_completion(self, messages: list[Message], tools_prompt: list) -> tuple[Message, str, int, list]:
        payload = {
            "messages": msg_list_to_llama_format(messages),
            "tools": tools_prompt,
            "tools_choice": "auto"
        }
        start_time = time.time()
        response = await self.client.post("", json=payload)
        end_time = time.time()
        result = response.json()
        print(result)
        result_msg = llama_format_to_msg(result['choices'][0]['message'])
        result_text = result_msg.content
        predicted_tokens = result['usage']['completion_tokens']
        result_msg.token_count = predicted_tokens
        generation_time = end_time - start_time
        print(f"[LLM]: Predicted tokens: {predicted_tokens}, Generation time: {generation_time:.2f} s, Speed: {predicted_tokens/generation_time:.2f} tok/s")
        tool_calls = []
        tool_calls_obj = result['choices'][0]['message']['tool_calls']
        if len(tool_calls_obj) > 0:
            tool_calls = self._openai_tool_calls_format(tool_calls_obj)
        return result_msg, result_text, predicted_tokens, tool_calls


    def _openai_tool_calls_format(self, tool_calls_object):
        tool_calls = []
        for tc in tool_calls_object:
            tool_name = tc['function']['name']
            arguments = json.loads(tc['function']['arguments'])
            tool_calls.append({"name": tool_name, "parameters": arguments})
        return tool_calls