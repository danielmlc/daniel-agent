import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any

class EmailReader:
    """A tool to read emails from an IMAP server."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the EmailReader with server and login details.

        Args:
            config (Dict): A dictionary containing 'imap_server', 'email_address', and 'password'.
        """
        self.imap_server = config.get("imap_server")
        self.email_address = config.get("email_address")
        self.password = config.get("password")
        if not all([self.imap_server, self.email_address, self.password]):
            raise ValueError("IMAP server, email address, and password are required.")

        self.mail = None

    def connect(self):
        """Connects and logs in to the IMAP server."""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"Failed to connect or log in to IMAP server: {e}")

    def disconnect(self):
        """Logs out and closes the connection."""
        if self.mail and self.mail.state == 'SELECTED':
            self.mail.close()
        if self.mail and self.mail.state != 'LOGOUT':
            self.mail.logout()

    def fetch_emails(self, mailbox: str = "inbox", criteria: str = "UNSEEN") -> List[Dict[str, Any]]:
        """
        Fetches emails from the specified mailbox based on criteria.

        Args:
            mailbox (str): The mailbox to fetch from (e.g., "inbox").
            criteria (str): The search criteria (e.g., "UNSEEN", "ALL").

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an email.
        """
        if not self.mail or self.mail.state != 'AUTH':
             self.connect()

        self.mail.select(mailbox)
        status, messages = self.mail.search(None, criteria)
        if status != "OK":
            raise RuntimeError(f"Failed to search emails: {messages}")

        email_list = []
        for num in messages[0].split():
            status, data = self.mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            from_ = msg.get("From")

            email_data = {"subject": subject, "from": from_, "body": ""}

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                            email_data["body"] = body
                            break
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                    email_data["body"] = body
                except:
                    pass

            email_list.append(email_data)

        return email_list

import socket

# Verification block
if __name__ == '__main__':
    print("--- Testing EmailReader Tool ---")
    # This test will intentionally fail because credentials are fake.
    # The goal is to verify that the class structure is correct and that
    # it raises a ConnectionError or a related network error as expected.
    test_config = {
        "imap_server": "imap.example.com",
        "email_address": "test@example.com",
        "password": "fakepassword"
    }

    try:
        email_reader = EmailReader(config=test_config)
        print("EmailReader initialized successfully.")
        email_reader.connect() # This line is expected to fail
    except ValueError as e:
        print(f"Test failed with ValueError, which is unexpected here: {e}")
    except (ConnectionError, imaplib.IMAP4.error, socket.gaierror) as e:
        print(f"Test gracefully failed with a network-related error as expected: {e}")
    except Exception as e:
        print(f"An unexpected and unhandled error occurred: {e}")
    finally:
        print("--- Test Finished ---")