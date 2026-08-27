"""FastAPI application factory: wires together auth/data/project routers,
the background build worker, the weekly scheduler, and the MCP server."""
import logging
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import auth, data, pages, projects
from app.core.build_runner import start_worker
from app.core.database import init_db
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.mcp_server import mcp

logging.basicConfig(level=logging.INFO)

mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_worker()
    start_scheduler()
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(mcp_app.router.lifespan_context(mcp_app))
        yield
    shutdown_scheduler()


app = FastAPI(title="Mikura - Universal Cap Packaging System", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/mcp", mcp_app)

app.include_router(auth.router)
app.include_router(data.router)
app.include_router(projects.router)
app.include_router(pages.router)


@app.get("/")
async def root():
    return {"service": "mikura", "status": "ok"}
