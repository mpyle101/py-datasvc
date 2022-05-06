import aiohttp

from typing import Any, List
from aiohttp import ClientSession
from fastapi import (
    status, APIRouter, Depends, HTTPException, Request, Response
)

from .. import deps
from . import graphql
from .params import QueryType, QueryParams
from ...core.config import settings
from ...schemas import AddTag, Datasets, DatasetEnvelope

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

ADD_TAG      = graphql.AddTagFactory()
REMOVE_TAG   = graphql.RemoveTagFactory()
GET_ALL      = graphql.GetAllFactory("DATASET", QUERY_VALUES)
GET_BY_ID    = graphql.GetOneFactory("dataset", QUERY_VALUES)
GET_BY_NAME  = graphql.NameFactory("DATASET", QUERY_VALUES)
GET_BY_TAGS  = graphql.TagsFactory("DATASET", QUERY_VALUES)
GET_BY_QUERY = graphql.QueryFactory("DATASET", QUERY_VALUES)

OPERATIONS = {
    QueryType.ALL:   GET_ALL,
    QueryType.NAME:  GET_BY_NAME,
    QueryType.TAGS:  GET_BY_TAGS,
    QueryType.QUERY: GET_BY_QUERY
}

router = APIRouter()

@router.get("", response_model=Datasets)
async def by_query(
    req: Request,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve datasets by query parameter
    """
    params = QueryParams(req)
    body = OPERATIONS[params.type].body(params)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return Datasets.from_json(data["data"]["results"])


@router.get("/{dataset_id}", response_model=DatasetEnvelope)
async def by_id(
    dataset_id: str,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Retrieve a dataset by id
    """
    body = GET_BY_ID.body(dataset_id)
    resp = await session.post(settings.DATAHUB_GRAPHQL, json=body)
    if resp.status < 200 or resp.status > 299:
        text = await resp.text()
        raise HTTPException(status=resp.status, detail=text)

    data = await resp.json()
    return DatasetEnvelope.from_json(data["data"]["dataset"])


@router.post("/{dataset_id}/tags")
async def add_tag(
    dataset_id: str,
    payload: AddTag,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Add a tag to a dataset
    """
    body = ADD_TAG.body(payload.tag, dataset_id)
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


@router.delete("/{dataset_id}/tags/{tag_id}")
async def remove_tag(
    dataset_id: str,
    tag_id: str,
    response: Response,
    session: ClientSession = Depends(deps.get_session),
) -> Any:
    """
    Remove a tag from a dataset
    """
    body = REMOVE_TAG.body(tag_id, dataset_id)
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
