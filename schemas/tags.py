import json
from typing import List, Optional
from pydantic import BaseModel, Field

from .paging import Paging

class Tag(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]


class TagEnvelope(BaseModel):
    tag: Optional[Tag]

    @staticmethod
    def from_json(e):
        if e is not None:
            if "tag" in e: e = e["tag"]
            props = e["properties"]

            tag = Tag(
                id=e["urn"],
                name=props["name"] if props else None,
                description=props["description"] if props else None,
            )
        else:
            tag = None

        return TagEnvelope(tag=tag)


class Tags(BaseModel):
    data: Optional[List[TagEnvelope]]
    paging: Optional[Paging]

    @staticmethod
    def from_json(results):
        if results["__typename"] == "SearchResults":
            paging = Paging.from_json(results)
            data = [TagEnvelope.from_json(e["entity"]) for e in results["entities"]]
        else:
            paging = None
            data = [TagEnvelope.from_json(e) for e in results["entities"]]

        return Tags(data=data, paging=paging)
