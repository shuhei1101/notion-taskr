import os


src_dir = os.path.dirname(__file__)
project_root = os.path.dirname(src_dir)
log_dir = os.path.join(project_root, 'log')

# 出力ログレベル
LOG_LEVEL = 'DEBUG'
# ログファイルの出力先
LOG_PATH = os.path.join(log_dir, 'app.log')
os.makedirs(log_dir, exist_ok=True)  # ログディレクトリが存在しない場合は作成

# NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_TOKEN = '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'
TASK_DB_ID = '1b08fe3c9ed280dab2f3c53738b9cdc8'

# 一人日の時間（単位：時間）
MAN_HOUR_PER_DAY = 8.0  


