class Persona:
    def __init__(self):
        self.name: str | None = None
        self.description: str | None = None
        self.traits: list[str] | None = []
        self.rules: list[str] | None = []
        self.system_prompt_template: str | None = None
        self.system_prompt: str | None = None

    def compile(self):
        if self.name is not None:
            self.system_prompt = self.system_prompt_template.format(
                name = self.name,
                description = self.description,
                traits = ", ".join(self.traits),
                rules = ", ".join(self.rules)
            )
            print(f"[Persona]: Loaded prompt: {self.system_prompt}")
        else:
            print("f[Persona]: Failed to compile prompt.")