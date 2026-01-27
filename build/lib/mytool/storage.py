import json
from pathlib import Path

DATA_FILE = Path.home() / ".todo.json"

def load_tasks():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2))
