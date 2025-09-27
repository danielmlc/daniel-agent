# main.py
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from core.orchestrator import PersonalButler
from core.config import load_config
from core.security import SecurityManager
# from core.health import SystemHealthMonitor # To be implemented in a later phase

# --- Web UI Configuration ---
app = FastAPI(
    title="Personal AI Assistant",
    description="智能个人助理系统",
    version="2.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dummy class for unimplemented health monitor
class DummySystemHealthMonitor:
    async def start_monitoring(self):
        logger.info("SystemHealthMonitor is not yet implemented. Skipping.")
    async def shutdown(self):
        logger.info("SystemHealthMonitor shutdown not required.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application lifespan: startup sequence initiated.")
    # 启动时初始化
    config = load_config()

    # For testing, override the token if it's a placeholder
    if config.agents.github_assistant.github_token == "YOUR_GITHUB_TOKEN_HERE":
        logger.warning("Using a dummy GitHub token for startup verification.")
        config.agents.github_assistant.github_token = "DUMMY_TOKEN"

    security_manager = SecurityManager(config.security.encryption.encryption_key)
    health_monitor = DummySystemHealthMonitor() # Placeholder

    # 初始化个人管家
    personal_butler = PersonalButler(config, security_manager)
    await personal_butler.initialize()

    # 启动后台任务
    asyncio.create_task(personal_butler.start_scheduler())
    asyncio.create_task(health_monitor.start_monitoring())

    app.state.butler = personal_butler
    app.state.health_monitor = health_monitor

    yield

    # 关闭时清理
    logger.info("Application lifespan: shutdown sequence initiated.")
    await personal_butler.shutdown()
    await health_monitor.shutdown()

# Re-assign the lifespan to the app instance
app.router.lifespan_context = lifespan

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # The root now redirects to the dashboard
    return templates.TemplateResponse("redirect.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serves the main dashboard page."""
    # We can pass data to the template here in the future
    return templates.TemplateResponse("dashboard.html", {"request": request, "page_title": "Dashboard"})

# This check is for when you run the script directly, e.g., for debugging.
# The standard way to run a FastAPI app is with `uvicorn main:app`.
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")
    uvicorn.run(app, host="0.0.0.0", port=8000)