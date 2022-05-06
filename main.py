#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.logger import logger

from .api.v1 import api_router
from .core import client, settings

async def on_start_up() -> None:
    logger.info("Creating session")
    client.get_session()

async def on_shutdown() -> None:
    logger.info("Closing session")
    await client.close_session()

app = FastAPI(
    title=settings.PROJECT_NAME,
    on_start_up=[on_start_up],
    on_shutdown=[on_shutdown],
)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
