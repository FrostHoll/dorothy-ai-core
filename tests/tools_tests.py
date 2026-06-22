from app.domain.entities.message import Message
from app.infrastructure.llm.llm_with_tools import LLMWithTools
from app.infrastructure.llm.lms_engine import LMSEngine
from app.infrastructure.tools.classes.GetWebpageTool import GetWebpageTool
from app.infrastructure.tools.classes.ListToolsTool import ListToolsTool
from app.infrastructure.tools.classes.RollNumberTool import RollNumberTool
from app.infrastructure.tools.classes.WebSearchTool import WebSearchTool
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_container import ToolContainer
from app.infrastructure.tools.tool_proxy import ToolProxy
import asyncio

async def main():
    container = ToolContainer()
    TextPostprocessor.tool_container = container
    container.register_tool(ToolProxy(ListToolsTool, tool_container=container), True)
    container.register_tool(ToolProxy(GetWebpageTool), True)
    container.register_tool(ToolProxy(WebSearchTool), True)
    container.register_tool(ToolProxy(RollNumberTool))

    model = LLMWithTools(LMSEngine(), container)

    history = [Message(role="system",
                       content="You are an AI assistant, who can use tools. If tool is malfunctioning, alert user and do not hallucinate the answer.")]

    while True:
        user_input = input(">>>")

        if user_input.startswith("!enable"):
            _, tool_name = user_input.split()
            try:
                container.enable_tool(tool_name)
            except ValueError as e:
                print(str(e))
            finally:
                continue
        if user_input.startswith("!list_tools"):
            print(container.get_all_tools())
            continue

        history.append(Message(role="user", content=user_input))

        msgs, response, _ = await model.create_chat_completion_with_tools(history)

        history.extend(msgs)

        for r in response:
            print(r)

if __name__ == "__main__":
    asyncio.run(main())