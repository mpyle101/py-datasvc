import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Depends, HTTPException, Request, Response

from .datasets import QUERY_VALUES as DATASET_VALUES
from .params import QueryParams
from . import graphql
from .. import deps
from ...core.config import settings
from ...schemas import AddTag, Datasets, Platforms, PlatformEnvelope

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

GET_ALL   = graphql.PlatformsFactory(QUERY_VALUES)
GET_BY_ID = graphql.GetOneFactory("tag", QUERY_VALUES)
DATASETS_BY_PLATFORM = graphql.FilterFactory("platorm", "DATASET", DATASET_VALUES)

router = APIRouter()

@router.get("", response_model=Platforms)
async def by_query(
    req: Request,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve all platforms
    """
    params = QueryParams(req)
    body = GET_ALL.body(params)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Platforms.from_json(data["data"]["results"]["modules"])


@router.get("/{platform_id}", response_model=PlatformEnvelope)
async def by_id(
    platform_id: str,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve a platform by id
    """
    body = GET_BY_ID.body(platform_id)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return PlatformEnvelope.from_json(data["data"]["dataPlatform"])


@router.get("/{platform_id}/datasets", response_model=Datasets)
async def datasets_by_platform(
    platform_id: str,
    req: Request,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets for the platform
    """
    params = QueryParams(req)
    body = DATASETS_BY_PLATFORM.body(platform_id, params)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Datasets.from_json(data["data"]["results"])
