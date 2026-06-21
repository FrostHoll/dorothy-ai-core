from app.infrastructure.llm.llama_engine import LlamaEngine
from app.infrastructure.tools.classes.GetWebpageTool import GetWebpageTool
from app.infrastructure.tools.classes.ListToolsTool import ListToolsTool
from app.infrastructure.tools.classes.RollNumberTool import RollNumberTool
from app.infrastructure.tools.classes.WebSearchTool import WebSearchTool
from app.infrastructure.tools.text_postprocessor import TextPostprocessor
from app.infrastructure.tools.tool_container import ToolContainer
from app.infrastructure.tools.tool_proxy import ToolProxy

if __name__ == "__main__":
    container = ToolContainer()
    TextPostprocessor.tool_container = container
    container.register_tool(ToolProxy(ListToolsTool, tool_container=container), True)
    container.register_tool(ToolProxy(GetWebpageTool), True)
    container.register_tool(ToolProxy(WebSearchTool), True)
    container.register_tool(ToolProxy(RollNumberTool))

    model = LlamaEngine(container)

    history = [{"role": "system", "content": "You are an AI assistant, who can use tools. If tool is malfunctioning, alert user and do not hallucinate the answer."}]

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

        history.append({"role": "user", "content": user_input})

        _, response, _ = model.create_chat_completion(history)

        history.append({"role": "assistant", "content": response})

        if "tool_call" in response:
            while "tool_call" in response:
                clean_text, tool_calls = TextPostprocessor.process_tool_calls(response)
                print(tool_calls)
                print(clean_text)
                for tool_call in tool_calls:
                    try:
                        result = container.execute(tool_call)
                        print(result)
                        history.append({"role": "assistant", "content": f"response:{tool_call["name"]}{{{result}}}"})
                    except Exception as e:
                        print(f"Tool execution failure: {str(e)}")
                        history.append({"role": "assistant",
                                        "content": f"Failure during execution of tool {tool_call["name"]}: {str(e)}"})

                _, response, _ = model.create_chat_completion(history)
        else:
            print(response)
            continue

        print(response)