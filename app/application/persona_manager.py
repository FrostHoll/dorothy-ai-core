import json

from app.domain.entities.persona import Persona
from app.core.config import PersonaManagerConfig as Config


class PersonaManager:
    def __init__(self):
        self.current_persona: Persona | None = None

    def get_persona(self) -> Persona | None:
        if self.current_persona is None:
            self.load_persona()
        return self.current_persona

    def load_persona(self):
        path = Config.directory + Config.persona_file

        with open(path, 'r', encoding='utf-8') as file_handle:
            persona_obj = json.load(file_handle)
        if persona_obj is not None:
            self.current_persona = Persona()
            self.current_persona.name = persona_obj['name']
            self.current_persona.description = persona_obj['description']
            self.current_persona.traits = persona_obj['traits']
            self.current_persona.rules = persona_obj['rules']
            self.current_persona.system_prompt_template = persona_obj['system_prompt_template']
            self.current_persona.compile()
        else:
            print("[PersonaManager]: Failed to load Persona.")