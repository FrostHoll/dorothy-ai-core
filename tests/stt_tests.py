import asyncio
import httpx

if __name__ == "__main__":
    client = httpx.AsyncClient(
        base_url="http://localhost:8083/api"
    )

    async def test():
        payload = {
            "voice_session_id": "1234",
            "text": "Привет! Расскажи, как прошел твой день? Надо озвучить 10 предложений."
        }
        response = await client.post("/synthesize", json=payload)
        response.raise_for_status()
        wav_bytes = response.content

        with open("E://test_tts.wav", "wb") as f:
            f.write(wav_bytes)

    asyncio.run(test())


