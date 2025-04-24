from flask import Flask, render_template
import logging

from application.task_application_service import TaskApplicationService

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update-excuted-task-id")
def update_excuted_task_id():
    '''実績タスクのIDを付与する'''
    try:
        TaskApplicationService().add_id_to_excuted_task()
        return "Task ID updated successfully!"
    except Exception as e:
        app.logger.error(f"Error occurred while updating task ID: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route("/update-man-days")
def update_man_days():
    '''予定タスクに予実工数を付与する'''
    try:
        TaskApplicationService().update_man_days()
        return "Man days updated successfully!"
    except Exception as e:
        app.logger.error(f"Error occurred while updating man days: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
