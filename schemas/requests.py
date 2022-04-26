from typing import Optional
from pydantic import BaseModel

class AddTag(BaseModel):
    tag: str


class CreateTag(BaseModel):
    name: str
    description: Optional[str]