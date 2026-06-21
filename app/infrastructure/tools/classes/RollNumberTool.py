import random
from typing import Any

from app.infrastructure.tools.tool_abc import ToolABC
from app.infrastructure.tools.tool_parameter import ToolParameter


class RollNumberTool(ToolABC):
    def __init__(self):
        super().__init__()
        self._parameters = [
            ToolParameter("maxRange", "integer", "Maximum value of the range. Inclusive.")
        ]

    def get_description(self) -> str:
        return "Get random number in range from 0 to 100 by default."

    def get_name(self) -> str:
        return "roll_number"

    async def _execute(self, params: dict[str, str]) -> Any:
        max_range = 100
        if "maxRange" in params:
            max_range = int(params["maxRange"])
        return random.randint(0, max_range)

    def get_display_text(self, params: dict[str, str]) -> str:
        max_range = 100
        if "maxRange" in params:
            max_range = params["maxRange"]
        return f"| Генерирую случайное число от 0 до {max_range}... |"