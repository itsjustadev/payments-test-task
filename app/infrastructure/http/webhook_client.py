async def send_webhook(client, url: str, payload: dict) -> bool:
    try:
        response = await client.post(url, json=payload)
        return 200 <= response.status_code < 300
    except Exception:
        return False
