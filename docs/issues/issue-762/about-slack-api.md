# Slack APIについて

## API一覧
Slack APIには主に以下の種類があります：

1. **Web API**
   - `chat.postMessage`: メッセージを送信
   - `chat.update`: 既存のメッセージを更新
   - `chat.delete`: メッセージを削除
   - `files.upload`: ファイルをアップロード
   - `users.list`: ユーザー一覧を取得
   - `channels.list`: チャンネル一覧を取得

2. **Events API**
   - Slackで発生したイベント（メッセージ、リアクションなど）をリアルタイムに受信

3. **RTM (Real Time Messaging) API**
   - WebSocketを使用してリアルタイムイベントを受信・送信

4. **Incoming Webhooks**
   - 最も簡単にSlackにメッセージを送信する方法
   - 特定のURLにPOSTリクエストを送信するだけでメッセージを投稿可能

## 初期セットアップ

### 1. Slack Appの作成
1. [Slack API](https://api.slack.com/apps)にアクセス
2. 「Create New App」ボタンをクリック
3. 「From scratch」を選択
4. アプリ名とワークスペースを入力して「Create App」をクリック

### 2. 権限の設定
1. 左メニューの「OAuth & Permissions」をクリック
2. 「Scopes」セクションまでスクロール
3. 「Bot Token Scopes」で以下の権限を追加：
   - `chat:write`: メッセージ送信権限
   - `chat:write.public`: パブリックチャンネルへのメッセージ送信権限
   - `channels:read`: チャンネル情報の取得権限（必要に応じて）

### 3. アプリのインストールとトークンの取得
1. 左メニューの「Install App」をクリック
2. 「Install to Workspace」ボタンをクリック
3. 権限を確認し「許可する」をクリック
4. 「OAuth & Permissions」ページに戻り、「Bot User OAuth Token」をコピー
   - このトークンを環境変数やconfig設定として安全に保存

### 4. Incoming Webhookの設定（簡易通知の場合）
1. 左メニューの「Incoming Webhooks」をクリック
2. 「Activate Incoming Webhooks」をオンに切り替え
3. ページ下部の「Add New Webhook to Workspace」をクリック
4. 通知を送信するチャンネルを選択して「許可する」をクリック
5. 生成されたWebhook URLをコピー
   - このURLを環境変数やconfig設定として安全に保存

## 通知を送信する基本的なコード例

### Python（requests使用）

```python
import requests
import json

def send_slack_notification(message):
    # Bot Tokenを使用する方法
    token = "xoxb-your-bot-token"
    channel = "#your-channel"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": channel,
        "text": message
    }
    
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.status_code == 200

# 使用例
send_slack_notification("タスクの開始5分前です！")
```

### Webhook URLを使用する方法（より簡単）

```python
import requests
import json

def send_slack_webhook(message):
    webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    
    payload = {
        "text": message
    }
    
    response = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    
    return response.status_code == 200

# 使用例
send_slack_webhook("タスクの開始5分前です！")
```

## セキュリティ上の注意点
- APIトークンやWebhook URLは公開リポジトリにコミットしないこと
- 環境変数または暗号化された設定ファイルで管理すること
- 必要最小限の権限のみを付与すること
