"""Telegram sender. Token and chat come from the environment, never from VCS."""
import json
import os
import urllib.request


class TelegramConfigError(RuntimeError):
    pass


class TelegramSender:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    @classmethod
    def from_env(cls):
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise TelegramConfigError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        return cls(token, chat_id)

    def send(self, text):
        """Send one message; raises on any failure."""
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data=json.dumps({"chat_id": self.chat_id, "text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"Telegram answered HTTP {response.status}")
