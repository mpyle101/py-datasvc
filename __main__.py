#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI

from .core import settings

if __name__ == "__main__":
    uvicorn.run("compendium.main:app", host=settings.HOST, port=settings.PORT)