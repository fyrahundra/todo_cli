import json
from pathlib import Path

DATA_FILE = Path.home() / ".todo.json"

def load_tasks():
    if not DATA_FILE.exists():
        return []

    tasks = json.loads(DATA_FILE.read_text())

    for task in tasks:
        if "status" not in task:
            task["status"] = "done" if task.get("done") else "todo"
            task.pop("done", None)

    return tasks


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2))
