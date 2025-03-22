import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
