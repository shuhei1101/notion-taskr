import requests

from notiontaskr.notifier.notifiable import Notifiable


class SlackNotifier(Notifiable):
    """Slack通知を行うクラス"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def notify(self, message: str) -> None:
        """Slackにメッセージを送信する

        :raise ValueError: Slack通知に失敗した場合
        """

        payload = {"text": message}
        response = requests.post(self.webhook_url, json=payload)

        if response.status_code != 200:
            print(f"Slack通知に失敗しました: {response.status_code} - {response.text}")
