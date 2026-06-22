from abc import ABC, abstractmethod
from app.infrastructure.tools.tool_parameter import ToolParameter
from typing import Any

class ToolABC(ABC):
    def __init__(self):
        self._parameters: list[ToolParameter] = []

    @property
    def parameters(self):
        return self._parameters

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    async def _execute(self, params: dict[str, str]) -> Any:
        pass

    def close(self) -> None:
        pass

    @abstractmethod
    def get_display_text(self, params: dict[str, str]) -> str:
        pass

    async def execute(self, params: dict[str, str]) -> Any:
        for par in self.parameters:
            if par.required and par.name not in params:
                raise ValueError(f"Incorrect format: missing required argument \'{par.name}\'")
        return await self._execute(params)

    def get_tool_info(self) -> dict:
        params_info = {}
        required = []
        for p in self.parameters:
            params_info.update(p.get_param_info())
            if p.required:
                required.append(p.name)
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": {
                    "type": "object",
                    "properties": params_info,
                    "required": required
                }
            }
        }