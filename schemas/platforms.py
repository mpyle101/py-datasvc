from typing import List, Optional
from pydantic import BaseModel

from schemas.paging import Paging

class Platform(BaseModel):
    id: str
    type: str
    name: str
    title: str


class PlatformEnvelope(BaseModel):
    platform: Optional[Platform]

    @staticmethod
    def from_json(e):
        props = e["properties"]
        return PlatformEnvelope(
            platform = Platform(
                id=e["urn"],
                name=e["name"],
                type=props["type"],
                title=props["title"]
            )
        )


class Platforms(BaseModel):
    data: Optional[List[PlatformEnvelope]]
    paging: Optional[Paging]

    @staticmethod
    def from_json(modules):
        platforms = [m for m in modules if m["moduleId"] == "Platforms"][0]
        data = [PlatformEnvelope.from_json(e) for e in platforms]

        return Platforms(data=data, paging=None)