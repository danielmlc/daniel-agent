from typing import Dict, List, Any
import asyncio
from datetime import datetime, timedelta

from core.base_agent import BaseAgent
from tools.github_tools import GitHubAPI

class GithubAssistant(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("github_assistant", config)
        self.github_api = GitHubAPI(token=self.config.get('github_token'))
        self.repositories = self.config.get('repositories', [])

    def calculate_time_range(self, time_range_str: str) -> str:
        """Calculates the 'since' timestamp string based on a time range like '24h'."""
        if isinstance(time_range_str, str) and time_range_str.endswith('h'):
            hours = int(time_range_str.strip('h'))
            since_time = datetime.utcnow() - timedelta(hours=hours)
        elif isinstance(time_range_str, str) and time_range_str.endswith('d'):
            days = int(time_range_str.strip('d'))
            since_time = datetime.utcnow() - timedelta(days=days)
        else: # Default to 24 hours
            since_time = datetime.utcnow() - timedelta(hours=24)
        return since_time.isoformat(timespec='seconds') + 'Z'

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the GitHub data collection task."""
        time_range = task.get('time_range', '24h')
        analysis_depth = task.get('analysis_depth', self.config.get('analysis_depth', 'basic'))

        results = {
            'summary': {},
            'detailed_activities': [],
            'insights': {},
            'recommendations': []
        }

        since_timestamp = self.calculate_time_range(time_range)

        for repo in self.repositories:
            repo_data = await self.analyze_repository(repo, since_timestamp, analysis_depth)
            results['detailed_activities'].extend(repo_data['activities'])
            results['summary'][repo] = repo_data['summary']

        results['insights'] = await self.generate_insights(results['detailed_activities'])
        results['recommendations'] = await self.generate_recommendations(results['insights'])

        return results

    async def analyze_repository(self, repo: str, since: str, depth: str) -> Dict[str, Any]:
        """Analyzes a single repository."""
        commits, pull_requests, issues = await asyncio.gather(
            self.github_api.get_commits(repo, since=since),
            self.github_api.get_pull_requests(repo),
            self.github_api.get_issues(repo, since=since)
        )

        activities = []
        since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))

        for commit in commits:
            activities.append({
                'type': 'commit', 'repo': repo, 'message': commit['commit']['message'],
                'author': commit['commit']['author']['name'], 'timestamp': commit['commit']['author']['date'],
            })

        for pr in pull_requests:
            pr_created_at = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
            if pr_created_at > since_dt:
                activities.append({
                    'type': 'pull_request', 'repo': repo, 'title': pr['title'],
                    'state': pr['state'], 'author': pr['user']['login'], 'timestamp': pr['created_at'],
                })

        summary = {
            'commit_count': len(commits),
            'new_pr_count': len([pr for pr in activities if pr['type'] == 'pull_request']),
            'issue_count': len(issues),
        }

        return {'activities': activities, 'summary': summary}

    async def generate_insights(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates smart insights (placeholder)."""
        return {'status': "Analysis pending."}

    async def generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generates recommendations (placeholder)."""
        return ["Review repository activity."]

    async def fallback_strategy(self, task: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        self.logger.warning(f"GitHub Assistant fallback due to: {error}")
        return {
            'message': 'GitHub service is temporarily unavailable.',
            'suggestion': 'Please check your GitHub token and repository names.',
            'error': str(error)
        }

    async def close_sessions(self):
        """Closes the underlying tool's session."""
        await self.github_api.close_session()

# Example usage for verification
async def main():
    print("--- Testing GitHubAssistant Agent ---")
    from core.config import load_config

    try:
        config = load_config()
        # Use a copy to avoid modifying the original object
        agent_config = config.agents.github_assistant.copy()
        # Ensure we use a dummy token for this test
        agent_config['github_token'] = 'DUMMY_TOKEN_FOR_VERIFICATION'
    except (FileNotFoundError, AttributeError):
        print("Config file not found or incomplete. Using a dummy config.")
        agent_config = {
            'github_token': 'DUMMY_TOKEN_FOR_VERIFICATION',
            'repositories': ['octocat/Hello-World']
        }

    agent = GitHubAssistant(agent_config)
    task = {'time_range': '24h'}

    result = await agent.execute_with_fallback(task)

    print(f"Agent execution finished with status: {result['status']}")
    if result['status'] == 'fallback':
        print("Fallback strategy was executed as expected.")
        print(f"Error message: {result.get('data', {}).get('error')}")
        assert '401' in result.get('error', '')
    else:
        print(f"Agent execution succeeded, which was NOT expected. Data: {result.get('data')}")

    await agent.close_sessions()
    print("--- Test Finished ---")

if __name__ == '__main__':
    asyncio.run(main())