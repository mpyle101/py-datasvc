import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Body, Depends, HTTPException, Response

from api import deps
from api.v1 import queries
from api.v1.datasets import QUERY_VALUES as DATASET_VALUES
from core.config import settings
from schemas import AddTag, Datasets, Platforms, PlatformEnvelope

QUERY_VALUES: str = """
    urn
    __typename
    ... on DataPlatform {
        name
        properties {
            type
            name: displayName
        }
    }
"""

QUERY_BY_ID: str     = queries.by_id("dataPlatform", QUERY_VALUES)
QUERY_BY_NAME: str   = queries.by_name(QUERY_VALUES)
QUERY_PLATFORMS: str = queries.platforms(QUERY_VALUES)
DATASETS_BY_PLATFORM: str = queries.by_query(DATASET_VALUES)

router = APIRouter()

@router.get("", response_model=Platforms)
async def by_query(
    limit: int = 10,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve all platforms
    """    
    body = {
        "query": QUERY_PLATFORMS,
        "variables": { 
            "input": {
                "userUrn": "urn:li:corpuser:datahub",
                "limit": limit,
                "requestContext": {
                    "scenario": "HOME"
                }
            }
        }
    }

    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Platforms.from_json(data["data"]["results"]["modules"])


@router.get("/{urn}", response_model=PlatformEnvelope)
async def by_id(
    session: ClientSession = Depends(deps.get_session),
    urn: str = None
) -> Any:
    """
    Retrieve a platform by id
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
    return PlatformEnvelope.from_json(data["data"]["dataPlatform"])


@router.get("/{pid}/datasets", response_model=Datasets)
async def datasets_by_platform(
    pid: str,
    limit: int = 10,
    offset: int = 0,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets for the platform
    """
    input = {
        "type": "DATASET",
        "query": "*",
        "start": offset,
        "count": limit,
        "filters": {
            "field": "platform",
            "value": pid
        }
    }
    body = {
        "query": DATASETS_BY_PLATFORM,
        "variables": { "input": input },
    }
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Datasets.from_json(data["data"]["results"])
