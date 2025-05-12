from flask import Flask, render_template

app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-deployment-tasks")
def update_executed_task_id():
    """デプロイ時に実行するタスクを実行する"""
    from notiontaskr.job import run_deployment_tasks

    run_deployment_tasks()
    return "Deployment tasks executed successfully!"


if __name__ == "__main__":
    # update_executed_task_id()
    app.run(host="0.0.0.0", port=5000, debug=True)
