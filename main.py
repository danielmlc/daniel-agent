# main.py
import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.orchestrator import PersonalButler
from core.config import load_config
from core.security import SecurityManager
# from core.health import SystemHealthMonitor # To be implemented in a later phase

# Configure basic logging
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

app = FastAPI(
    title="Personal AI Assistant",
    description="智能个人助理系统",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Personal AI Assistant is running."}

# This check is for when you run the script directly, e.g., for debugging.
# The standard way to run a FastAPI app is with `uvicorn main:app`.
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")
    uvicorn.run(app, host="0.0.0.0", port=8000)