import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Depends, HTTPException, Response

from api import deps
from api.v1 import queries
from core.config import settings
from schemas import Datasets, DatasetEnvelope

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
    session: ClientSession = Depends(deps.get_session),
    name: str = None,
    query: str = None,
    limit: int = 10,
    offset: int = 0
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


@router.get("/{urn}", response_model=DatasetEnvelope)
async def by_id(
    session: ClientSession = Depends(deps.get_session),
    urn: str = None
) -> Any:
    """
    Retrieve a dataset by id
    """
    body = {
        "query": QUERY_BY_ID,
        "variables": { "urn": urn },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return DatasetEnvelope.from_json(data["data"]["dataset"])


@router.post("/{urn}/tags", status_code=status.HTTP_201_CREATED)
async def add_tag(
    session: ClientSession = Depends(deps.get_session),
    urn: str = None
) -> Any:
    """
    Retrieve a dataset by id
    """
    body = {
        "query": QUERY_BY_ID,
        "variables": { "urn": urn },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return DatasetEnvelope.from_json(data["data"]["dataset"])


@router.delete("/{urn}/tags/{tag_id}")
async def remove_tag(
    urn: str,
    tag_id: str,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve a dataset by id
    """
    body = {
        "query": QUERY_REMOVE_TAG,
        "variables": { "tagUrn": tag_id, "resourceUrn": urn },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status == status.HTTP_200_OK:
        result = await resp.json()
        if "data" in result:
            if result["data"]["success"]:
                response.status = status.HTTP_
    else:
        text = await resp.text()
        response.status = resp.status
        raise HTTPException(status=resp.status, detail=text)
