import asyncio
from flask import Flask, render_template

from notiontaskr.application.task_application_service import TaskApplicationService

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-daily-task")
def update_executed_task_id():
    """dayly_taskを実行するエンドポイント"""
    service = TaskApplicationService()
    asyncio.run(service.daily_task())

    return "dayly task executed successfully!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
