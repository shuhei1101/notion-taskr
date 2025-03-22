from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.auth import verify_google_token
import os
import requests

bp = Blueprint("routes", __name__)  # ルーティング用のBlueprintを作成

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

@bp.route("/")
def home():
    token = request.cookies.get("token")
    email = verify_google_token(token)
    
    if not email:
        return redirect(url_for("routes.login"))
    
    return render_template("macros.html", email=email)

@bp.route("/login")
def login():
    return "Google OAuth でログインしてください"

@bp.route("/execute_macro", methods=["POST"])
def execute_macro():
    macro_id = request.form.get("macro_id")
    notion_url = f"https://api.notion.com/v1/pages/{macro_id}"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    data = {"properties": {"Status": {"select": {"name": "Done"}}}}

    response = requests.patch(notion_url, json=data, headers=headers)
    return jsonify({"status": response.status_code, "data": response.json()})
