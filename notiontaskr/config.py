import os
import emoji

from notiontaskr.notifier.slack_notifier import SlackNotifier

# ==================== ディレクトリ設定 ====================
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")

# ディレクトリが存在しない場合は作成
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ==================== デバッグ設定 ====================
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in (
    "true",
    "1",
    "yes",
)  # デバッグモードの有効化


# ==================== ログ設定 ====================
LOG_LEVEL = "DEBUG"  # 出力ログレベル
LOG_PATH = os.path.join(LOG_DIR, "app.log")  # ログファイルの出力先


# ==================== Notion API設定 ====================
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASK_DB_ID = os.getenv("TASK_DB_ID")

# ==================== Slack API設定 ====================
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # SlackのWebhook URL
NOTIFIER = SlackNotifier(webhook_url=SLACK_WEBHOOK_URL)  # type: ignore
DEFAULT_BEFORE_START_MINUTES = 5  # 開始前通知のデフォルト時間（分）
DEFAULT_BEFORE_END_MINUTES = 5  # 終了前通知のデフォルト時間（分）

# ==================== pickleファイル設定 ====================
BUCKET_NAME = "notion-api-bucket"  # GCSバケット名
# ローカルのpickleファイルの保存先
LOCAL_SCHEDULED_PICKLE_PATH = os.path.join(CACHE_DIR, "scheduled_task.pkl")
# ローカルの実績タスクpickleファイルの保存先
LOCAL_EXECUTED_PICKLE_PATH = os.path.join(CACHE_DIR, "executed_task.pkl")
BUCKET_SCHEDULED_PICKLE_PATH = (
    "/notion-api/cache/scheduled_task.pkl"  # GCSのpickleファイルの保存先
)
BUCKET_EXECUTED_PICKLE_PATH = (
    "/notion-api/cache/executed_task.pkl"  # GCSの実績タスクpickleファイルの保存先
)

# ==================== タスク名ラベル設定 ====================
# 名前ラベルの絵文字（例: [⏱️0/2]）
ID_EMOJI = emoji.emojize(":label:")
MAN_HOURS_EMOJI = emoji.emojize(":stopwatch:")
PARENT_ID_EMOJI = emoji.emojize(":deciduous_tree:")
REMIND_EMOJI = emoji.emojize(":bell:")

# 動作確認用
if __name__ == "__main__":
    print(emoji.demojize("🔔"))
    print(emoji.emojize(":bell:"))
