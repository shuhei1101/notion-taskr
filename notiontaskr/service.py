import asyncio
from datetime import datetime
from flask import Flask, render_template, request

from notiontaskr.application.task_application_service import TaskApplicationService

from notiontaskr.util.converter import dt_to_month_start_end

service = TaskApplicationService()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-daily-task")
def update_executed_task_id():
    """dayly_taskを実行するエンドポイント"""

    asyncio.run(service.daily_task())

    return "dayly task executed successfully!"


@app.route("/uptime_from_start_end", methods=["GET"])
def get_uptime_from_start_end():
    """uptimeを取得するエンドポイント

    タグ配列、開始日、終了日をクエリパラメータとして受け取る
    例: https://example.com/uptime_from_start_end?tags=tag1&start_year=2024&start_month=12&end_year=2025&end_month=1
    """
    tags = request.args.getlist("tags")
    start_year = request.args.get("start_year")
    start_month = request.args.get("start_month")
    end_year = request.args.get("end_year")
    end_month = request.args.get("end_month")

    if not tags or not start_year or not start_month or not end_year or not end_month:
        return "Invalid parameters", 400

    start_of_month = datetime(year=int(start_year), month=int(start_month), day=1)
    end_dt = datetime(year=int(end_year), month=int(end_month), day=1)
    _, end_of_month = dt_to_month_start_end(end_dt)

    uptime_data_by_tag = asyncio.run(
        service.get_uptime(from_=start_of_month, to=end_of_month, tags=tags)
    )

    # レスポンスをJSON形式で返す
    return uptime_data_by_tag.to_json(), 200


@app.route("/uptime_from_month", methods=["GET"])
def get_uptime_from_month():
    """uptimeを取得するエンドポイント

    タグ配列、年月をクエリパラメータとして受け取る
    例: https://example.com/uptime_from_month?tags=tag1&year=2024&month=12
    """
    tags = request.args.getlist("tags")
    year = request.args.get("year")
    month = request.args.get("month")

    if not tags or not year or not month:
        return "Invalid parameters", 400

    dt = datetime(year=int(year), month=int(month), day=1)
    start, end = dt_to_month_start_end(dt)

    uptime_data_by_tag = asyncio.run(
        service.get_uptime(
            from_=start,
            to=end,
            tags=tags,
        )
    )

    # レスポンスをJSON形式で返す
    return uptime_data_by_tag.to_json(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
