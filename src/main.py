from flask import Flask, render_template
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-deployment-tasks")
def update_executed_task_id():
    '''実績タスクのIDを付与する'''
    from job import run_deployment_tasks
    run_deployment_tasks()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
