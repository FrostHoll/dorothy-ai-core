import json


class Settings:
    discord_token: str = ""
    core_client_base_url: str = ""

    @staticmethod
    def get_settings():
        with open("discord_service\\config.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            _settings = Settings()
            _settings.discord_token = data['discord-token']
            _settings.core_client_base_url = data['core-client-base-url']
            return _settings

settings = Settings.get_settings()