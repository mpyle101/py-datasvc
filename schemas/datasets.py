from typing import List, Optional
from pydantic import BaseModel

from schemas.tags import TagEnvelope
from schemas.paging import Paging

class Field(BaseModel):
    path: str
    type: str
    native: str

    @staticmethod
    def from_json(f):
        return Field(**f)


class Dataset(BaseModel):
    id: str
    path: str
    type: Optional[str]
    name: Optional[str]
    origin: Optional[str]
    platform: Optional[str]
    platformType: Optional[str]
    platformName: Optional[str]
    tags: List[TagEnvelope]
    fields: Optional[List[Field]]


class DatasetEnvelope(BaseModel):
    dataset: Optional[Dataset]

    @staticmethod
    def from_json(e):
        if e is not None:
            st = e["subTypes"]
            props = e["properties"]
            platform = e["platform"]
            fields = e["schema"]["fields"] if e["schema"] else None
            tags = e["tags"]["tags"] if e["tags"] else None

            dataset = Dataset(
                id=e["urn"],
                path=e["name"],
                type=st["names"][0] if st else None,
                name=props["name"] if props else None,
                origin=props["origin"] if props else None,
                platform=platform["name"] if platform else None,
                platformName=platform["properties"]["name"] if platform else None,
                platformType=platform["properties"]["type"] if platform else None,
                tags=[TagEnvelope.from_json(t) for t in tags] if tags else [],
                fields=[Field.from_json(f) for f in fields] if fields else None,
            )
        else:
            dataset = None

        return DatasetEnvelope(dataset=dataset)


class Datasets(BaseModel):
    data: Optional[List[DatasetEnvelope]]
    paging: Optional[Paging]

    @staticmethod
    def from_json(results):
        if results["__typename"] == "SearchResults":
            data = [DatasetEnvelope.from_json(e["entity"]) for e in results["entities"]]
            paging = Paging.from_json(results)
        else:
            data = [DatasetEnvelope.from_json(e) for e in results["entities"]]
            paging = None

        return Datasets(data=data, paging=paging)