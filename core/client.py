import aiohttp

from typing import Optional

from core.config import settings

class Client:
    session: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls.session is None:
            cls.session = aiohttp.ClientSession(
                headers=settings.DATAHUB_HEADERS
            )

        return cls.session

    
    @classmethod
    async def close_session(cls) -> None:
        if cls.session:
            await cls.session.close()
            cls.session = None


def get_session() -> aiohttp.ClientSession:
    return Client.get_session()

async def close_session() -> None:
    await Client.close_session()