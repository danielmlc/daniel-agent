from typing import Dict, List, Any
import asyncio

from core.base_agent import BaseAgent
from tools import email_tools

class EmailProcessor(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("email_processor", config)
        self.accounts = self.config.get('email_accounts', [])

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the email processing task for all configured accounts.
        Ensures connections are closed after each account is processed.
        """
        all_new_emails = []
        for account_config in self.accounts:
            account_id = account_config.get("provider", account_config.get("email_address"))
            if not account_id:
                self.logger.warning("Skipping an email account due to missing provider/address.")
                continue

            email_reader = None
            try:
                self.logger.info(f"Processing emails for account: {account_id}")
                email_reader = email_tools.EmailReader(account_config)

                # Using asyncio.to_thread to run the synchronous imaplib code
                new_emails = await asyncio.to_thread(email_reader.fetch_emails, criteria="UNSEEN")

                self.logger.info(f"Found {len(new_emails)} new emails for {account_id}.")
                for email in new_emails:
                    email['account'] = account_id # Add account info to the result
                all_new_emails.extend(new_emails)

            except Exception as e:
                self.logger.error(f"Failed to process emails for {account_id}: {e}")
                # We continue to the next account instead of failing the whole task
            finally:
                if email_reader and email_reader.mail:
                    self.logger.info(f"Closing connection for account: {account_id}")
                    await asyncio.to_thread(email_reader.disconnect)

        return {
            "new_emails_count": len(all_new_emails),
            "emails": all_new_emails
        }

    async def fallback_strategy(self, task: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        self.logger.warning(f"Email Processor fallback due to: {error}")
        return {
            'message': 'Email processing failed for one or more accounts.',
            'suggestion': 'Please check the IMAP configuration and credentials for your email accounts.',
            'error': str(error)
        }

    async def close_sessions(self):
        """Closes any open email connections."""
        for account_id, tool in self.email_tools.items():
            self.logger.info(f"Disconnecting email tool for account: {account_id}")
            if tool.mail:
                await asyncio.to_thread(tool.disconnect)

from unittest.mock import patch, MagicMock

# --- Enhanced Verification Block with Mocking ---
async def main():
    print("--- Testing EmailProcessor Agent with Mocking ---")

    # 1. Define a mock config
    test_config = {
        "enabled": True,
        "email_accounts": [{
            "provider": "mock_gmail",
            "imap_server": "mock.server.com",
            "email_address": "mock@test.com",
            "password": "mockpassword"
        }]
    }

    # 2. Define the fake email our mock tool will return
    fake_emails = [{
        "subject": "Test Subject",
        "from": "sender@test.com",
        "body": "This is a test email."
    }]

    # 3. Use 'patch' to replace the real EmailReader with a mock
    with patch('agents.email_processor.email_tools.EmailReader') as MockEmailReader:
        # Configure the instance that will be created
        mock_instance = MagicMock()
        mock_instance.fetch_emails.return_value = fake_emails
        mock_instance.mail = True # Simulate an active connection
        MockEmailReader.return_value = mock_instance

        # 4. Initialize and run the agent
        agent = EmailProcessor(config=test_config)
        result = await agent.execute({})

        # 5. Assert the success path
        print("Verifying agent processed mock data correctly...")
        assert result['new_emails_count'] == 1
        assert result['emails'][0]['subject'] == "Test Subject"
        assert result['emails'][0]['account'] == "mock_gmail"
        print("✅ Success path test PASSED.")

        # 6. Assert that the tool was used correctly
        print("Verifying that the email tool was initialized and used...")
        MockEmailReader.assert_called_once_with(test_config['email_accounts'][0])
        mock_instance.fetch_emails.assert_called_once_with(criteria="UNSEEN")
        print("✅ Tool usage test PASSED.")

        # 7. Assert that the connection was closed (resource leak check)
        print("Verifying that the connection was closed...")
        mock_instance.disconnect.assert_called_once()
        print("✅ Resource leak test PASSED.")

    print("--- All tests finished successfully! ---")

if __name__ == '__main__':
    # We need to add this import for the test block
    from unittest.mock import patch, MagicMock
    asyncio.run(main())