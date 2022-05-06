from typing import Generator
from ..core import client

async def get_session() -> Generator:
    return client.get_session()
