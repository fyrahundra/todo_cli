import typer

from typing import Dict, Optional

from mytool.storage import load_tasks, save_tasks

from rich.console import Console
from rich.table import Table

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.styles import Style
from prompt_toolkit.application import run_in_terminal

console = Console()
app = typer.Typer(help="A simple todo CLI")

def kanban_select():
    tasks = load_tasks() or []  # allow empty board
    for t in tasks:
        t.setdefault("status", "todo")  # ensure old tasks have a status

    STATUSES = ["todo", "doing", "done"]
    current_col = 0
    selected = 0

    def tasks_by_status(status):
        return [t for t in tasks if t.get("status") == status]

    def get_text():
        lines = []
        max_rows = max(len(tasks_by_status(s)) for s in STATUSES) or 1

        # help line at the top
        lines.append(("", "[a] add  [x] →  [z] ←  [r] remove  [s] save  [esc] cancel  [space] inspect\n\n"))

        # header
        headers = []
        for i, s in enumerate(STATUSES):
            style = "reverse" if i == current_col else ""
            headers.append((style, f" {s.upper():^20} "))
        lines.append(("", "".join(h[1] for h in headers) + "\n"))

        # tasks
        for row in range(max_rows):
            for col, status in enumerate(STATUSES):
                col_tasks = tasks_by_status(status)
                if row < len(col_tasks):
                    task = col_tasks[row]
                    text_main = f"{task['text'][:13]:13}..." if len(task['text']) > 16 else f"{task['text']:16}"
                else:
                    text_main = " " * 16

                cursor = "➤ " if (col == current_col and row == selected) else "  "
                style = "reverse" if (col == current_col and row == selected) else ""
                text = f"{cursor}{text_main}"
                lines.append((style, f"{text} "))
            lines.append(("", "\n"))

        return lines

    kb = KeyBindings()

    @kb.add("up")
    def _up(event):
        nonlocal selected
        selected = max(0, selected - 1)
        event.app.invalidate()

    @kb.add("down")
    def _down(event):
        nonlocal selected
        col_tasks = tasks_by_status(STATUSES[current_col])
        if col_tasks:
            selected = min(len(col_tasks) - 1, selected + 1)
        event.app.invalidate()

    @kb.add("left")
    def _left(event):
        nonlocal current_col, selected
        current_col = max(0, current_col - 1)
        selected = 0
        event.app.invalidate()

    @kb.add("right")
    def _right(event):
        nonlocal current_col, selected
        current_col = min(len(STATUSES) - 1, current_col + 1)
        selected = 0
        event.app.invalidate()

    @kb.add("x")
    def _move_forward(event):
        nonlocal selected
        col_tasks = tasks_by_status(STATUSES[current_col])
        if not col_tasks:
            return
        task = col_tasks[selected]
        task["status"] = STATUSES[min(current_col + 1, len(STATUSES) - 1)]
        selected = selected - 1 if selected > 0 else 0
        event.app.invalidate()

    @kb.add("z")
    def _move_back(event):
        nonlocal selected
        col_tasks = tasks_by_status(STATUSES[current_col])
        if not col_tasks:
            return
        task = col_tasks[selected]
        task["status"] = STATUSES[max(current_col - 1, 0)]
        selected = selected - 1 if selected > 0 else 0
        event.app.invalidate()

    @kb.add("r")
    @kb.add("backspace")
    def _remove(event):
        nonlocal selected
        col_tasks = tasks_by_status(STATUSES[current_col])
        if not col_tasks:
            return
        task = col_tasks[selected]
        tasks.remove(task)
        selected = max(0, selected - 1)
        event.app.invalidate()

    @kb.add("a")
    def _add(event):
        def get_task_text():
            text = input("New task text: ")
            description = input("New task description: ")
            return text, description

        def add_new_task():
            text, description = get_task_text()
            if text.strip() != "":
                tasks.append({"text": text.strip(), "done": False, "status": STATUSES[current_col], "description": description.strip() if description.strip() != "" else None})

        run_in_terminal(add_new_task)
        event.app.invalidate()
    
    @kb.add("space")
    @kb.add("i")
    def _inspect(event):
        nonlocal selected
        col_tasks = tasks_by_status(STATUSES[current_col])
        if not col_tasks:
            return
        task = col_tasks[selected]

        def inspect_task():
            console.print(f"\n[bold]Task Details[/]")
            console.print(f"Text: {task['text']}")
            console.print(f"Status: {task['status']}")
            if 'description' in task and task['description'] is not None:
                console.print(f"Description: {task['description']}\n") 
            return input("Press Enter to continue...")

        run_in_terminal(inspect_task)
        event.app.invalidate()

    @kb.add("s")
    @kb.add("enter")
    def _accept(event):
        run_in_terminal(lambda: console.clear())
        event.app.exit(result=True)

    @kb.add("escape")
    def _cancel(event):
        run_in_terminal(lambda: console.clear())
        event.app.exit(result=False)

    control = FormattedTextControl(
        get_text,
        focusable=True,
        show_cursor=False
    )

    window = Window(content=control)

    app_tui = Application(
        layout=Layout(window),
        key_bindings=kb,
        full_screen=True,
        style=Style.from_dict({"reverse": "reverse"}),
        erase_when_done=True,
    )

    confirmed = app_tui.run()

    if confirmed:
        save_tasks(tasks)
        console.print("[bold green]✔ Tasks updated[/]")
    else:
        console.print("[bold red]X Cancelled[/]")

@app.command()
def run():
    """Interactively manage tasks"""
    kanban_select()


def main():
    app()
