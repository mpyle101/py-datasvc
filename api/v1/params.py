from enum import auto, Enum
from lib2to3.pgen2.token import NAME
from fastapi import Request

class QueryType(Enum):
    ALL = auto()
    NAME = auto()
    TAGS = auto()
    QUERY = auto()

class QueryParams:
    def __init__(self, req: Request):
        params = req.query_params()

        self.limit = params.get("limit", 10)
        self.start = params.get("offset", 0)

        if "query" in params:
            self.type = QueryType.QUERY
            self.query = params["query"]
        elif "name" in params:
            self.type = QueryType.NAME
            self.query = params["name"]
        elif "tags" is not None:
            self.type = QueryType.TAGS
            self.query = params["tags"]
        else:
            self.type = QueryType.ALL
