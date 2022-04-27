import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Depends, HTTPException, Response

from api import deps
from api.v1 import queries
from api.v1.datasets import QUERY_VALUES as DATASET_VALUES
from core.config import settings
from schemas import tags, CreateTag, Datasets, Tags, Tag, TagEnvelope

QUERY_VALUES: str = """
    urn
    __typename
    ... on Tag {
        urn
        properties {
            name
            description
        }
    }
"""

QUERY_BY_ID: str     = queries.by_id("tag", QUERY_VALUES)
QUERY_BY_NAME: str   = queries.by_name(QUERY_VALUES)
QUERY_BY_QUERY: str  = queries.by_query(QUERY_VALUES)
DATASETS_BY_TAG: str = queries.by_query(DATASET_VALUES)

router = APIRouter()

@router.get("", response_model=Tags)
async def by_query(
    name: str = None,
    query: str = None,
    limit: int = 10,
    offset: int = 0,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve tags by query parameter
    """
    if query is not None:
        operation = QUERY_BY_QUERY
        input = {"type": "TAG", "query": f"*{query}*", "start": offset, "count": limit}
    elif name is not None:
        operation = QUERY_BY_NAME
        input = {"type": "TAG", "query": name, "limit": limit}
    else:
        # Get all tags
        operation = QUERY_BY_QUERY
        input = {"type": "TAG", "query": "*", "start": offset, "count": limit}
    
    body = {
        "query": operation,
        "variables": { "input": input },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise aiohttp.web.HTTPException(status=resp.status, text=text)

    data = await resp.json()
    return Tags.from_json(data["data"]["results"])


@router.get("/{tid}", response_model=TagEnvelope)
async def by_id(
    tid: str,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve a tag by id
    """
    body = {
        "query": QUERY_BY_ID,
        "variables": { "urn": tid },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return TagEnvelope.from_json(data["data"]["tag"])


@router.get("/{tid}/datasets", response_model=Datasets)
async def datasets_by_tag(
    tid: str,
    limit: int = 10,
    offset: int = 0,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets with the tag
    """
    input = {
        "type": "DATASET",
        "query": "*",
        "start": offset,
        "count": limit,
        "filters": {
            "field": "tags",
            "value": tid
        }
    }
    body = {
        "query": DATASETS_BY_TAG,
        "variables": { "input": input },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Datasets.from_json(data["data"]["results"])


@router.post("", response_model=TagEnvelope)
async def create_tag(
    tag: CreateTag,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Create a new tag
    """
    body = queries.create_tag(tag.name, tag.description)
    resp = await session.post(settings.DATAHUB_INGEST, json=body)
    if resp.status == status.HTTP_200_OK:
        response.status = status.HTTP_201_CREATED
        return TagEnvelope(
            tag=Tag(
                id=f"urn:li:tag:{tag.name}",
                name=tag.name,
                description=tag.description
            )
        )
    else:
        text = await resp.text()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=text)


@router.delete("/{tid}")
async def delete_tag(
    tid: str,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Delete a specified tag
    """
    body = queries.delete_tag(tid)
    resp = await session.post(settings.DATAHUB_INGEST, json=body)
    if resp.status == status.HTTP_200_OK:
        response.status = status.HTTP_204_NO_CONTENT
    else:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

