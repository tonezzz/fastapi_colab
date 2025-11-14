"""Simple CLI for managing the local _todo.yml file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, TypedDict

import yaml


def default_path() -> Path:
    return Path("_todo.yml")


class Task(TypedDict):
    task: str
    status: str


def load_tasks(path: Path) -> List[Task]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data:
        return []
    return list(data)


def save_tasks(path: Path, tasks: List[Task]) -> None:
    path.write_text(yaml.safe_dump(tasks, sort_keys=False), encoding="utf-8")


def list_tasks(path: Path) -> None:
    tasks = load_tasks(path)
    if not tasks:
        print("(no tasks)")
        return
    for idx, task in enumerate(tasks, start=1):
        print(f"{idx}. {task['task']} [status: {task['status']}]")


def add_task(path: Path, description: str, status: str) -> None:
    tasks = load_tasks(path)
    tasks.append({"task": description, "status": status})
    save_tasks(path, tasks)
    print(f"Added task: {description} ({status})")


def update_status(path: Path, index: int, status: str) -> None:
    tasks = load_tasks(path)
    if index < 1 or index > len(tasks):
        raise IndexError("Task index out of range")
    tasks[index - 1]["status"] = status
    save_tasks(path, tasks)
    print(f"Updated task {index} → {status}")


def delete_task(path: Path, index: int) -> None:
    tasks = load_tasks(path)
    if index < 1 or index > len(tasks):
        raise IndexError("Task index out of range")
    removed = tasks.pop(index - 1)
    save_tasks(path, tasks)
    print(f"Deleted task {index}: {removed['task']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage _todo.yml entries.")
    parser.add_argument("command", choices=["list", "add", "status", "delete"])
    parser.add_argument("value", nargs="?")
    parser.add_argument("extra", nargs="?")
    parser.add_argument(
        "--path",
        type=Path,
        default=default_path(),
        help="Path to the YAML todo file (default: _todo.yml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = args.path
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.command == "list":
        list_tasks(path)
    elif args.command == "add":
        if not args.value:
            raise ValueError("Provide a description for the task.")
        status = args.extra or "pending"
        add_task(path, args.value, status)
    elif args.command == "status":
        if not args.value or not args.extra:
            raise ValueError("Provide index and new status, e.g., status 1 done")
        update_status(path, int(args.value), args.extra)
    elif args.command == "delete":
        if not args.value:
            raise ValueError("Provide index to delete")
        delete_task(path, int(args.value))


if __name__ == "__main__":
    main()
