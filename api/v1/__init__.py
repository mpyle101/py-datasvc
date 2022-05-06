from fastapi import APIRouter

from . import datasets
from . import platforms
from . import tags

api_router = APIRouter()
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["platforms"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])