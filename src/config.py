import os

import emoji


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

# 名前ラベルの絵文字（例: [⏱️0/2]）
ID_EMOJI = emoji.emojize(':label:')
MAN_HOURS_EMOJI = emoji.emojize(':stopwatch:')
PARENT_ID_EMOJI = emoji.emojize(':deciduous_tree:')

# 動作確認用
if __name__ == '__main__':
    print(emoji.demojize("🏷️"))
    print(emoji.emojize(':label:'))