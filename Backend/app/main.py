from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration import settings
from app.API.health_routes import router as health_router
from app.API.chat_routes import router as chat_router
from app.API.approval_routes import router as approval_router


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Advanced AI Agent with Planning, "
        "Tools, Memory, MCP, Multi-Agent Workflow "
        "and Human-in-the-Loop"
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api/v1"
)

app.include_router(
    chat_router,
    prefix="/api/v1"
)

app.include_router(
    approval_router,
    prefix="/api/v1"
)


@app.get("/")
async def root():

    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs"
    }