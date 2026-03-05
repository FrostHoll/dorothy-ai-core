import hashlib


class ExternalIDCompiler:
    @staticmethod
    def compile(user_id: int, channel_id: int, guild_id: int) -> str:
        # --- Full identification ---
        # raw = f"{user_id}:{channel_id}:{guild_id}"
        # --- user_id only ---
        # raw = str(user_id)
        # --- channel_id + guild_id ---
        raw = f"{channel_id}:{guild_id}"
        return hashlib.sha256(raw.encode()).hexdigest()