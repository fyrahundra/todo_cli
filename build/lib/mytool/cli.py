import typer
from mytool.storage import load_tasks, save_tasks

app = typer.Typer(help="A simple todo CLI")

def add_task(text: str):
    tasks = load_tasks()
    tasks.append({"text": text, "done": False})
    save_tasks(tasks)
    typer.echo(f"Added: {text}")

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        typer.echo("No tasks yet!")
        raise typer.Exit()

    for i, task in enumerate(tasks, start=1):
        status = "✔" if task["done"] else " "
        typer.echo(f"{i}. [{status}] {task['text']}")

def mark_done(number: int):
    tasks = load_tasks()
    try:
        tasks[number - 1]["done"] = True
    except IndexError:
        typer.echo("Invalid task number")
        raise typer.Exit(code=1)

    save_tasks(tasks)
    typer.echo("Task marked as done")

@app.command()
def add(text: str):
    """Add a new task"""
    add_task(text)

@app.command(name="list")
def _list():
    """List tasks"""
    list_tasks()

@app.command()
def done(number: int):
    """Mark a task as done"""
    mark_done(number)

def main():
    app()
