import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import status, APIRouter, Depends, HTTPException, Request, Response

from api import deps
from api.v1 import graphql, queries
from api.v1.datasets import QUERY_VALUES as DATASET_VALUES
from api.v1.params import QueryParams, QueryType
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

GET_ALL         = graphql.GetAllFactory(QUERY_VALUES)
GET_BY_ID       = graphql.GetOneFactory("tag", QUERY_VALUES)
GET_BY_NAME     = graphql.NameFactory(QUERY_VALUES)
GET_BY_QUERY    = graphql.QueryFactory(QUERY_VALUES)
DATASETS_BY_TAG = graphql.FilterFactory("tags", "DATASET", DATASET_VALUES)

OPERATIONS = {
    QueryType.ALL:   GET_ALL,
    QueryType.NAME:  GET_BY_NAME,
    QueryType.QUERY: GET_BY_QUERY
}

router = APIRouter()

@router.get("", response_model=Tags)
async def by_query(
    req: Request,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve tags by query parameter
    """
    params = QueryParams(req)
    body = OPERATIONS[params.type].body(params)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise aiohttp.web.HTTPException(status=resp.status, text=text)

    data = await resp.json()
    return Tags.from_json(data["data"]["results"])


@router.get("/{tag_id}", response_model=TagEnvelope)
async def by_id(
    tag_id: str,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve a tag by id
    """
    body = GET_BY_ID.body(tag_id)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return TagEnvelope.from_json(data["data"]["tag"])


@router.get("/{tag_id}/datasets", response_model=Datasets)
async def datasets_by_tag(
    tag_id: str,
    req: Request,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets with the tag
    """
    params = QueryParams(req)
    body = DATASETS_BY_TAG.body(tag_id, params)
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

