class ToolParameter:
    def __init__(self, name: str, param_type: str, description: str, required: bool = False, enum: list[str] | None = None):
        self.name = name
        self.param_type = param_type
        self.description = description
        self.required = required
        self.enum = enum

    def get_param_info(self) -> dict:
        if self.enum is not None:
            return {self.name: {"type": self.param_type, "description": self.description, "enum": self.enum}}
        return {self.name: {"type": self.param_type, "description": self.description}}