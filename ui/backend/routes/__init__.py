"""API routes."""

from fastapi import APIRouter

from .compile import router as compile_router
from .infer import router as infer_router
from .prompts import router as prompts_router
from .sessions import router as sessions_router
from .testcases import router as testcases_router

api_router = APIRouter()

api_router.include_router(sessions_router, tags=["sessions"])
api_router.include_router(prompts_router, tags=["prompts"])
api_router.include_router(compile_router, tags=["compile"])
api_router.include_router(infer_router, tags=["inference"])
api_router.include_router(testcases_router, tags=["testcases"])
