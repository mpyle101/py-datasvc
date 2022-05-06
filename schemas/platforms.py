from typing import List, Optional
from pydantic import BaseModel

from .paging import Paging

class Platform(BaseModel):
    id: str
    type: str
    name: str
    title: str


class PlatformEnvelope(BaseModel):
    platform: Optional[Platform]

    @staticmethod
    def from_json(e):
        print(e)
        props = e["properties"]
        return PlatformEnvelope(
            platform = Platform(
                id=e["urn"],
                name=e["name"],
                type=props["type"],
                title=props["name"]
            )
        )


class Platforms(BaseModel):
    data: Optional[List[PlatformEnvelope]]
    paging: Optional[Paging]

    @staticmethod
    def from_json(modules):
        platforms = [m for m in modules if m["id"] == "Platforms"][0]
        data = [PlatformEnvelope.from_json(e["entity"]) for e in platforms["content"]]

        return Platforms(data=data, paging=None)