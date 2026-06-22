from typing import Any

from app.infrastructure.tools.tool_proxy import ToolProxy


class ToolContainer:
    def __init__(self):
        self.tools: dict[str, ToolProxy] = {}
        self.active_tools: dict[str, ToolProxy] = {}

    def register_tool(self, tool: ToolProxy, enabled_by_default: bool = False):
        self.tools[tool.tool_class.__name__] = tool
        if enabled_by_default:
            self.enable_tool(tool.tool_class.__name__)

    def enable_tool(self, tool_name: str):
        if tool_name not in self.tools:
            raise ValueError(f"Tool named {tool_name} does not exist.")
        tool = self.tools[tool_name]
        tool.enable()
        self.active_tools[tool.get_name()] = tool

    async def disable_tool(self, tool_name: str):
        if tool_name not in self.tools:
            raise ValueError(f"Tool named {tool_name} does not exist.")
        tool = self.tools[tool_name]
        if tool.instance:
            if tool.get_name() in self.active_tools:
                self.active_tools.pop(tool.get_name())
        await tool.disable()

    async def execute(self, tool_call: dict[str, str | dict[str, str]]) -> Any:
        tool_name = tool_call["name"]
        if tool_name not in self.active_tools:
            raise ValueError(f"Tool named {tool_name} is not enabled or does not exist.")
        tool = self.active_tools[tool_name]
        result = await tool.execute(tool_call["parameters"])
        return result

    def get_all_tools(self) -> list[dict[str, bool]]:
        return [{tool_name: tool.is_enabled} for tool_name, tool in self.tools.items()]

    def get_tools_prompt(self) -> list:
        return [tool.get_tool_info() for _, tool in self.active_tools.items()]

    def get_tool_call_display_text(self, tool_name: str, params: dict[str, str]):
        if not tool_name in self.active_tools:
            return f"|Вызываю инструмент {tool_name}...|"
        display_text = self.active_tools[tool_name].get_display_text(params)
        return display_text