import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".todo_config.json"
DEFAULT_DATA_FILE = Path.home() / ".todo.json"

def get_data_file():
    """Get the current data file path, checking config first"""
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            if "data_file" in config:
                return Path(config["data_file"])
        except (json.JSONDecodeError, KeyError):
            pass
    return DEFAULT_DATA_FILE

def load_tasks():
    data_file = get_data_file()
    if not data_file.exists():
        return []

    tasks = json.loads(data_file.read_text())

    for task in tasks:
        if "status" not in task:
            task["status"] = "done" if task.get("done") else "todo"
            task.pop("done", None)

    return tasks


def save_tasks(tasks):
    data_file = get_data_file()
    data_file.write_text(json.dumps(tasks, indent=2))

def set_data_file(path: Path):
    """Update the data file path in config"""
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            pass
    config["data_file"] = str(path)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
