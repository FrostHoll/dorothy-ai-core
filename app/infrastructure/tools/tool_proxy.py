from typing import Any

from app.infrastructure.tools.tool_abc import ToolABC


class ToolProxy(ToolABC):
    def __init__(self, tool_class, *args, **kwargs):
        super().__init__()
        self.tool_class = tool_class
        self.init_args = args
        self.init_kwargs = kwargs

        self.instance: ToolABC | None = None
        self.is_enabled = False

    @property
    def parameters(self):
        if self.instance:
            return self.instance.parameters
        return self.parameters

    def enable(self):
        if not self.is_enabled:
            self.instance = self.tool_class(*self.init_args, **self.init_kwargs)
            self.is_enabled = True
            print(f"[ToolProxy]: Tool {self.tool_class.__name__} is enabled.")

    def disable(self):
        if self.instance:
            self.instance.close()
            self.instance = None
            self.is_enabled = False
            print(f"[ToolProxy]: Tool {self.tool_class.__name__} is disabled.")

    def get_name(self) -> str:
        self._check_enabled()
        return self.instance.get_name()

    def get_description(self) -> str:
        self._check_enabled()
        return self.instance.get_description()

    def _execute(self, params: dict[str, str]) -> Any:
        self._check_enabled()
        return self.instance._execute(params)

    def get_display_text(self, params: dict[str, str]) -> str | None:
        self._check_enabled()
        return self.instance.get_display_text(params)

    def _check_enabled(self):
        if not self.is_enabled or self.instance is None:
            raise RuntimeError(f"Requested tool {self.tool_class.__name__} is not enabled.")

    def __getattr__(self, item):
        self._check_enabled()

        return getattr(self.instance, item)