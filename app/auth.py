import os
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token):
    """Google IDトークンを検証し、メールアドレスを取得"""
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        return id_info["email"]
    except Exception:
        return None
