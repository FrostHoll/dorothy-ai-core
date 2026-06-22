from typing import Any

from app.infrastructure.tools.tool_abc import ToolABC
from app.infrastructure.tools.tool_container import ToolContainer


class ListToolsTool(ToolABC):
    def __init__(self, tool_container: ToolContainer):
        super().__init__()
        self.tool_container = tool_container

    def get_name(self) -> str:
        return "ListTools"

    def get_description(self) -> str:
        return "This tool returns list of all tools and their current state (enabled/disabled)."

    async def _execute(self, params: dict[str, str]) -> Any:
        return str(self.tool_container.get_all_tools())

    def get_display_text(self, params: dict[str, str]) -> str:
        return "| Смотрю доступные инструменты... |"