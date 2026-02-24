"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config import settings
from db.database import init_db
from utils.logger import setup_logger
from utils.cache import init_redis
from api.routes import chat, auth, knowledge, admin
from api.middleware.rate_limit import RateLimitMiddleware


# ── 生命周期管理 ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭时的生命周期钩子"""
    # 启动时
    setup_logger()
    await init_db()
    await init_redis()
    yield
    # 关闭时（清理资源）


# ── 应用初始化 ──────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description="基于 LLM 的智能客服系统 API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── 中间件注册 ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)

# ── 路由注册 ────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["认证"])
app.include_router(chat.router,      prefix="/api/chat",      tags=["对话"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(admin.router,     prefix="/api/admin",     tags=["管理"])


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
