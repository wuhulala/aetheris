import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from models.chat import OpenAIChatCompletionForm
from config import AGENTS_DIR
from routers import workspaces
from utils.job import generate_openai_chat_completion
from utils.loader import load_modules_from_directory, PIPELINE_MODULES, PIPELINES

if not os.path.exists(AGENTS_DIR):
    os.makedirs(AGENTS_DIR)


async def on_startup():
    await load_modules_from_directory(AGENTS_DIR)
    for module in PIPELINE_MODULES.values():
        if hasattr(module, "on_startup"):
            await module.on_startup()


async def on_shutdown():
    for module in PIPELINE_MODULES.values():
        if hasattr(module, "on_shutdown"):
            await module.on_shutdown()


async def reload():
    await on_shutdown()
    # Clear existing pipelines
    PIPELINES.clear()
    PIPELINE_MODULES.clear()
    # Load pipelines afresh
    await on_startup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(docs_url="/docs", redoc_url=None, lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspace"])


@app.middleware("http")
async def check_url(request: Request, call_next):
    start_time = int(time.time())
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/v1")
@app.get("/")
async def get_status():
    return {"status": True}


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def chat_completion(form_data: OpenAIChatCompletionForm):
    return await generate_openai_chat_completion(form_data)


@app.get("/health")
async def healthcheck():
    return {
        "status": True
    }


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9588)