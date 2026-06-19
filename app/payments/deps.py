from fastapi import Header, HTTPException, status


async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")) -> bool:
    """Проверка API ключа"""
    if not await verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return True
