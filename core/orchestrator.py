import asyncio
import logging
import importlib
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import load_config, AttrDict
from core.security import SecurityManager

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def to_camel_case(snake_str: str) -> str:
    """Converts snake_case string to CamelCase string."""
    return "".join(word.capitalize() for word in snake_str.split('_'))

class PersonalButler:
    def __init__(self, config: AttrDict, security_manager: SecurityManager):
        self.config = config
        self.security_manager = security_manager
        self.agents = {}
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger("PersonalButler")

    async def _load_agents(self):
        """Dynamically loads and initializes agents based on the configuration."""
        self.logger.info("Loading enabled agents...")
        for agent_name, agent_config in self.config.agents.items():
            if agent_config.get('enabled'):
                try:
                    module_name = f"agents.{agent_name}"
                    class_name = to_camel_case(agent_name)

                    agent_module = importlib.import_module(module_name)
                    agent_class = getattr(agent_module, class_name)

                    self.agents[agent_name] = agent_class(agent_config)
                    self.logger.info(f"Successfully loaded agent: {class_name}")
                except (ImportError, AttributeError) as e:
                    self.logger.error(f"Failed to load agent '{agent_name}': {e}")

    async def initialize(self):
        """Initializes the Personal Butler and its agents."""
        self.logger.info("Initializing Personal Butler...")
        await self._load_agents()

    async def _run_agent_task(self, agent_name: str):
        """Wrapper to run a specific agent's task."""
        agent = self.agents.get(agent_name)
        if agent:
            self.logger.info(f"Executing scheduled task for agent: {agent_name}")
            # The task dictionary can be expanded in the future
            task = {'trigger': 'scheduled'}
            result = await agent.execute_with_fallback(task)
            self.logger.info(f"Task for {agent_name} finished with status: {result['status']}")
        else:
            self.logger.warning(f"Attempted to run task for non-existent agent: {agent_name}")

    async def start_scheduler(self):
        """Configures and starts the task scheduler."""
        self.logger.info("Starting scheduler...")
        for agent_name, agent_config in self.config.agents.items():
            if agent_name in self.agents and 'schedule' in agent_config:
                self.scheduler.add_job(
                    self._run_agent_task,
                    'cron',
                    **{field: val for field, val in zip(['minute', 'hour', 'day', 'month', 'day_of_week'], agent_config.schedule.split())},
                    args=[agent_name],
                    id=agent_name
                )
                self.logger.info(f"Scheduled task for {agent_name} with cron: '{agent_config.schedule}'")

        if self.scheduler.get_jobs():
            self.scheduler.start()
        else:
            self.logger.warning("No jobs were scheduled.")

    async def shutdown(self):
        """Shuts down the scheduler and cleans up agent resources."""
        self.logger.info("Shutting down Personal Butler...")
        if self.scheduler.running:
            self.scheduler.shutdown()

        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'close_sessions'):
                self.logger.info(f"Closing sessions for agent: {agent_name}")
                await agent.close_sessions()

# Example usage for verification
async def main():
    print("--- Testing PersonalButler Orchestrator ---")
    config = load_config()

    # For testing purposes, override the token to prevent initialization errors
    if 'github_assistant' in config.agents and config.agents.github_assistant.enabled:
        config.agents.github_assistant.github_token = "DUMMY_TOKEN_FOR_TESTING"

    security = SecurityManager(config.security.encryption.encryption_key)

    butler = PersonalButler(config, security)
    await butler.initialize()

    # Assert that the enabled agent was loaded
    assert "github_assistant" in butler.agents
    print("Agent 'github_assistant' loaded successfully.")

    # Assert that disabled agents were not loaded
    assert "health_advisor" not in butler.agents
    print("Disabled agent 'health_advisor' was not loaded, as expected.")

    # We won't start the scheduler in this test, just check the agent list
    print(f"Number of loaded agents: {len(butler.agents)}")

    await butler.shutdown()
    print("PersonalButler shutdown complete.")
    print("--- Test Finished ---")

if __name__ == '__main__':
    asyncio.run(main())