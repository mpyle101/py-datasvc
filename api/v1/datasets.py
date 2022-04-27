import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Body, Depends, HTTPException, Response

from api import deps
from api.v1 import queries
from core.config import settings
from schemas import AddTag, Datasets, DatasetEnvelope

QUERY_VALUES: str = """
    urn
    __typename
    ... on Dataset {
        name
        platform {
            name
            properties {
                type
                name: displayName
            }
        }
        properties {
            name
            origin
        }
        schema: schemaMetadata {
            fields {
                type
                path: fieldPath
                native: nativeDataType
            }
        }
        subTypes {
            names: typeNames
        }
        tags {
            tags {
                tag {
                    urn
                    __typename
                    properties {
                        name
                        description
                    }
                }
            }
        }
    }
"""

QUERY_BY_ID: str      = queries.by_id("dataset", QUERY_VALUES)
QUERY_BY_NAME: str    = queries.by_name(QUERY_VALUES)
QUERY_BY_QUERY: str   = queries.by_query(QUERY_VALUES)
QUERY_ADD_TAG: str    = queries.add_tag()
QUERY_REMOVE_TAG: str = queries.remove_tag()

router = APIRouter()

@router.get("", response_model=Datasets)
async def by_query(
    tags: str = None,
    name: str = None,
    query: str = None,
    limit: int = 10,
    offset: int = 0,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets by query parameter
    """
    if query is not None:
        operation = QUERY_BY_QUERY
        input = {"type": "DATASET", "query": f"*{query}*", "start": offset, "count": limit}
    elif name is not None:
        operation = QUERY_BY_NAME
        input = {"type": "DATASET", "query": name, "limit": limit}
    elif tags is not None:
        operation = QUERY_BY_QUERY
        input = {"type": "DATASET", "query": f"tags:{query}", "start": offset, "count": limit}
    else:
        # Get all datasets
        operation = QUERY_BY_QUERY
        input = {"type": "DATASET", "query": "*", "start": offset, "count": limit}
    
    body = {
        "query": operation,
        "variables": { "input": input },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Datasets.from_json(data["data"]["results"])


@router.get("/{dsid}", response_model=DatasetEnvelope)
async def by_id(
    session: ClientSession = Depends(deps.get_session),
    dsid: str = None
) -> Any:
    """
    Retrieve a dataset by id
    """
    body = {
        "query": QUERY_BY_ID,
        "variables": { "urn": dsid },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return DatasetEnvelope.from_json(data["data"]["dataset"])


@router.post("/{dsid}/tags")
async def add_tag(
    dsid: str,
    tag: AddTag,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Add a tag to a dataset
    """
    body = {
        "query": QUERY_ADD_TAG,
        "variables": {
            "input": { "tagUrn": tag.tag, "resourceUrn": dsid }
        },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status == status.HTTP_200_OK:
        result = await resp.json()
        if "data" in result:
            if result["data"]["success"]:
                response.status = status.HTTP_204_NO_CONTENT
            else:
                response.status = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            response.status = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        text = await resp.text()
        response.status = resp.status
        raise HTTPException(status=resp.status, detail=text)


@router.delete("/{dsid}/tags/{tag_id}")
async def remove_tag(
    dsid: str,
    tag_id: str,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Remove a tag from a dataset
    """
    body = {
        "query": QUERY_REMOVE_TAG,
        "variables": {
            "input": { "tagUrn": tag_id, "resourceUrn": dsid }
        },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    print(f"RESP: {resp}")
    if resp.status == status.HTTP_200_OK:
        result = await resp.json()
        print(f"BODY: {result}")
        if "data" in result:
            if result["data"]["success"]:
                response.status = status.HTTP_204_NO_CONTENT
            else:
                response.status = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            response.status = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        text = await resp.text()
        response.status = resp.status
        raise HTTPException(status=resp.status, detail=text)
