import os
import emoji

# ------------- ディレクトリ設定 -------------
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
CACHE_DIR = os.path.join(PROJECT_DIR, "cache")

# ディレクトリが存在しない場合は作成
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


# ------------- ログ設定 -------------
LOG_LEVEL = "DEBUG"  # 出力ログレベル
LOG_PATH = os.path.join(LOG_DIR, "app.log")  # ログファイルの出力先


# ------------- Notion API設定 -------------
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASK_DB_ID = os.getenv("TASK_DB_ID")

# ------------- pickleファイル設定 -------------
BUCKET_NAME = "notion-api-bucket"  # GCSバケット名
LOCAL_SCHEDULED_PICKLE_PATH = os.path.join(
    CACHE_DIR, "scheduled_task.pkl"
)  # ローカルのpickleファイルの保存先
BUCKET_SCHEDULED_PICKLE_PATH = (
    "/notion-api/cache/scheduled_task.pkl"  # GCSのpickleファイルの保存先
)

# ------------- タスク名ラベル設定 -------------
# 名前ラベルの絵文字（例: [⏱️0/2]）
ID_EMOJI = emoji.emojize(":label:")
MAN_HOURS_EMOJI = emoji.emojize(":stopwatch:")
PARENT_ID_EMOJI = emoji.emojize(":deciduous_tree:")

# 動作確認用
if __name__ == "__main__":
    print(emoji.demojize("🏷️"))
    print(emoji.emojize(":label:"))
