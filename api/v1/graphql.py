from typing import Mapping
from api.v1 import queries
from api.v1.params import QueryParams

class AddTagFactory:
    def __init__(self, type: str, values: str):
        self.query = queries.add_tag()

    def body(self, tag: str, rsrc: str) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": { "tagUrn": tag, "resourceUrn": rsrc }
            }
        }


class RemoveTagFactory:
    def __init__(self, type: str, values: str):
        self.query = queries.remove_tag()

    def body(self, tag: str, rsrc: str) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": { "tagUrn": tag, "resourceUrn": rsrc }
            }
        }


class GetOneFactory:
    def __init__(self, type: str, values: str):
        self.query = queries.by_id(type, values)

    def body(self, id: str) -> Mapping:
        return {
            "operation": self.query,
            "variables": { "urn": id }
        }


class GetAllFactory:
    def __init__(self, type: str, values: str):
        self.type = type
        self.query = queries.by_query(values)

    def body(self, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": {
                    "type": type,
                    "query": "*",
                    "start": params.offset,
                    "count": params.limit
                }
            } 
        }


class NameFactory:
    def __init__(self, type: str, values: str):
        self.type = type
        self.query = queries.by_name(values)

    def body(self, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": {
                    "type": type,
                    "query": self.query,
                    "limit": params.limit
                }
            } 
        }


class TagsFactory:
    def __init__(self, type: str, values: str):
        self.type = type
        self.query = queries.by_query(values)

    def body(self, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": {
                    "type": type,
                    "query": f"tags:{self.query}",
                    "start": params.start,
                    "count": params.limit
                }
            } 
        }


class QueryFactory:
    def __init__(self, type: str, values: str):
        self.type = type
        self.query = queries.by_query(values)

    def body(self, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": {
                    "type": type,
                    "query": f"*{self.query}*",
                    "start": params.start,
                    "count": params.limit
                }
            } 
        }


class FilterFactory:
    def __init__(self, field: str, type: str, values: str):
        self.field = filter
        self.query = queries.by_query(values)

    def body(self, value: str, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": {
                "input": {
                    "type": type,
                    "query": "*",
                    "start": params.start,
                    "count": params.limit,
                    "filters": {
                        "field": self.field,
                        "value": value
                    }
                }
            } 
        }


class PlatformsFactory:
    def __init__(self, values: str):
        self.query = queries.platforms(values)

    def body(self, params: QueryParams) -> Mapping:
        return {
            "operation": self.query,
            "variables": { 
                "input": {
                    "userUrn": "urn:li:corpuser:datahub",
                    "limit": params.limit,
                    "requestContext": {
                        "scenario": "HOME"
                    }
                }
            }
        }
