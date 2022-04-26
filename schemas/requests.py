from pydantic import BaseModel

class AddTag(BaseModel):
    tag: str