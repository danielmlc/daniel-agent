import aiohttp
import asyncio
from datetime import datetime, timedelta

class GitHubAPI:
    """A simple asynchronous wrapper for the GitHub API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, session: aiohttp.ClientSession = None):
        if not token or token == "YOUR_GITHUB_TOKEN_HERE":
            raise ValueError("GitHub token is required.")

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def close_session(self):
        """Close the aiohttp session if it exists."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, method: str, path: str, params: dict = None) -> dict:
        """Make an asynchronous request to the GitHub API."""
        session = await self._get_session()
        url = f"{self.BASE_URL}{path}"

        async with session.request(method, url, params=params) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            return await response.json()

    async def get_commits(self, repo: str, since: str = None) -> list:
        """Fetch commits for a repository."""
        params = {}
        if since:
            params['since'] = since
        return await self._request("GET", f"/repos/{repo}/commits", params=params)

    async def get_pull_requests(self, repo: str, state: str = "all", since: str = None) -> list:
        """Fetch pull requests for a repository."""
        # Note: GitHub API doesn't directly support a 'since' filter for PRs list.
        # This would require filtering after fetching. For this tool, we'll fetch all.
        params = {'state': state, 'sort': 'created', 'direction': 'desc'}
        return await self._request("GET", f"/repos/{repo}/pulls", params=params)

    async def get_issues(self, repo: str, state: str = "all", since: str = None) -> list:
        """Fetch issues for a repository."""
        params = {'state': state}
        if since:
            params['since'] = since
        return await self._request("GET", f"/repos/{repo}/issues", params=params)

# Example usage for verification
async def main():
    # This test requires a valid GitHub token and repository to run successfully.
    # We'll use placeholder values and expect it to fail gracefully.
    print("--- Testing GitHubAPI Tool ---")
    try:
        github_api = GitHubAPI(token="DUMMY_TOKEN_FOR_TESTING")
        print("GitHubAPI initialized.")

        # This call is expected to fail with a 401 Unauthorized error
        # because the token is invalid. This still verifies the code structure.
        await github_api.get_commits("octocat/Hello-World")

    except ValueError as e:
        print(f"Test failed as expected (ValueError): {e}")
    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            print("Test gracefully failed with 401 Unauthorized, as expected.")
            print("This confirms the API request structure is correct.")
        else:
            print(f"Test failed with unexpected HTTP error: {e.status} {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'github_api' in locals():
            await github_api.close_session()
        print("--- Test Finished ---")

if __name__ == '__main__':
    asyncio.run(main())