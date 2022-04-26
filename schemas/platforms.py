from typing import List, Optional
from pydantic import BaseModel

class Paging(BaseModel):
    total: int
    limit: int
    offset: int


class Platform(BaseModel):
    id: str
    type: str
    name: str
    title: str


class PlatformEnvelope(BaseModel):
    platform: Optional[Platform]


class Platforms(BaseModel):
    data: Optional[List[PlatformEnvelope]]
    paging: Optional[Paging]
