import asyncio

import httpx

if __name__ == "__main__":
    client = httpx.AsyncClient(
        base_url="http://localhost:8082/api"
    )


    async def poll_result(job_id: str) -> str:
        result = None
        while True:
            await asyncio.sleep(2.0)
            response = await client.get(f"/get/{job_id}")
            response.raise_for_status()
            job_response = response.json()
            if job_response['status'] == "done":
                result = job_response['text']
                return result

