#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI

from .core import settings
from .main import app

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)