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

def load_tasks(db_name=None):
    """Load tasks from a specific database or all databases"""
    data_file = get_data_file()
    if not data_file.exists():
        return []

    content = json.loads(data_file.read_text())
    
    # Handle dict format (multiple databases)
    if isinstance(content, dict):
        if db_name:
            # Load specific database
            if db_name in content:
                tasks = content[db_name]
            else:
                tasks = []
        else:
            # Merge all databases into a single list
            merged_tasks = []
            for db_tasks in content.values():
                if isinstance(db_tasks, list):
                    merged_tasks.extend(db_tasks)
            tasks = merged_tasks
    # Handle list format (legacy single database)
    else:
        tasks = content
    
    # Migrate old format tasks to new format
    for task in tasks:
        if "status" not in task:
            task["status"] = "done" if task.get("done") else "todo"
            task.pop("done", None)

    return tasks

def load_db_names():
    """Load the names of all databases from the data file"""
    data_file = get_data_file()
    if not data_file.exists():
        return []

    content = json.loads(data_file.read_text())
    if isinstance(content, dict):
        return list(content.keys())
    return []

def save_tasks(tasks, db_name=None):
    """Save tasks to a specific database or as a single list"""
    data_file = get_data_file()
    if db_name:
        # Save to a specific database within dict structure
        all_tasks = {}
        if data_file.exists():
            try:
                existing = json.loads(data_file.read_text())
                if isinstance(existing, dict):
                    all_tasks = existing
            except json.JSONDecodeError:
                pass
        all_tasks[db_name] = tasks
        data_file.write_text(json.dumps(all_tasks, indent=2))
    else:
        # Save as a single list (legacy format)
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
