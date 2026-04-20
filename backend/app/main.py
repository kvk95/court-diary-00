import logging
import threading
import webbrowser
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api import api_router
from app.core.config import settings
from app.startup.load_settings import load_global_settings
from app.database.models.base.session import async_engine
from app.middleware.request_context_middleware import RequestContextMiddleware
from app.middleware.exception_handler import add_exception_handlers
from app.utils.logging_framework.queue_manager import get_queue_manager
from app.utils.logging_framework.sqlalchemy_listeners import attach_listeners

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # 1) Attach listeners for DB logging, Request Response
    attach_listeners(async_engine=async_engine)

    # 2) Start the logging queue workers
    qm = get_queue_manager()
    await qm.start()    

    print("✅ Logging Framework Started")

    # 3) startup 
    
    # start_scheduler(send_tomorrow_hearings_job)

    # Run blocking I/O in a thread during startup
    # ✅ Just await the async startup job
    # 🔑 Create DB session manually (no user, no Depends)
    async with async_sessionmaker(bind=async_engine)() as session:
        await load_global_settings(session)

    # FastAPI lifecycle enters running state
    # App is now ready to serve requests
    yield

    # Optional: cleanup logic here (shutdown)

    # 4) Shutdown logging framework
    await qm.stop()
    print("🛑 Logging Framework Stopped")


app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    lifespan=lifespan,
    swagger_ui_parameters={
        "deepLinking": True,
        "syntaxHighlight.theme": "monokai",
        "docExpansion": "none",  # Collapse all operations by default
        "filter": True,  # Enable the filter box
        "tagsSorter": "alpha",
    },
)

if settings.APP_ENV != "development":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.ngrok.io", "*.yourdomain.com"],
    )

# IMPORTANT:
# RequestContextMiddleware MUST be added before (outer to) all other middlewares.
# ASGI middleware execution order is reversed on entry; if this is not outermost,
# ContextVar mutations (user_id, request_id, etc.) may be lost for inner middleware
# and HTTP logging will see empty context.

app.add_middleware(RequestContextMiddleware)
add_exception_handlers(app=app)

app.include_router(api_router)

if settings.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.CORS_ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", tags=[__name__])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat() + "Z",
        "service": "courtdiary-api",
        "version": "1.0.0",
    }


def run():
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=False,  # we'll handle reload via command
        log_level="info",
    )


def run_dev():
    import time

    import uvicorn

    def open_browser_delayed():
        time.sleep(1.5)
        url = f"http://127.0.0.1:{settings.APP_PORT}{settings.DOCS_URL or '/docs'}"
        print(f"Opening Swagger UI: {url}")
        webbrowser.open_new_tab(url)

    if settings.APP_ENV == "development":
        threading.Thread(target=open_browser_delayed, daemon=True).start()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
        log_level="info",
    )


# This allows: poetry run dev
if __name__ == "__main__":
    run_dev()

# poetry run uvicorn app.main:app --reload
# poetry run dev        # dev with auto-open docs
# poetry run start      # production mode
