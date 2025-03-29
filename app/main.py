from flask import Flask, render_template

from application.task_applicaiton_service import TaskApplicationService

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update-actual-task-id")
def update_actual_task_id():
    '''実績タスクのIDを付与する'''
    TaskApplicationService().add_id_to_actual_task()

@app.route("/update-man-days")
def update_man_days():
    '''予定タスクに予実工数を付与する'''
    TaskApplicationService().update_man_days()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
