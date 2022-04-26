from pydantic import BaseModel

class Paging(BaseModel):
    total: int
    limit: int
    offset: int

    @staticmethod
    def from_json(data):
        return Paging(
            total=data["total"],
            limit=data["count"],
            offset=data["start"]
        )