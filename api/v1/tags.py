import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException, status

from api import deps
from api.v1 import queries
from api.v1.datasets import QUERY_VALUES as DATASET_VALUES
from core.config import settings
from schemas import Datasets, Tags, TagEnvelope

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
    session: ClientSession = Depends(deps.get_session),
    name: str = None,
    query: str = None,
    limit: int = 10,
    offset: int = 0
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


@router.get("/{urn}", response_model=TagEnvelope)
async def by_id(
    session: ClientSession = Depends(deps.get_session),
    urn: str = None
) -> Any:
    """
    Retrieve a tag by id
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
    return TagEnvelope.from_json(data["data"]["tag"])


@router.get("/{urn}/datasets", response_model=Datasets)
async def datasets_by_tag(
    session: ClientSession = Depends(deps.get_session),
    urn: str = None,
    limit: int = 10,
    offset: int = 0
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
            "value": urn
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