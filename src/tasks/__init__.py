"""
Task Package

This package provides reusable task components for browser automation.
Each task type is a separate, self-contained module that can be:
- Imported independently
- Used in other projects
- Tested in isolation
- Extended easily

Architecture:
    tasks/
    ├── __init__.py       (this file)
    ├── base_task.py      (abstract base)
    ├── url_task.py       (URL component)
    └── ai_task.py        (AI component)

Usage in other projects:
    from tasks import URLTask, AITask
    
    task = URLTask(url="https://example.com")
    result = task.execute(comet_path="...")
"""

from .base_task import BaseTask, TaskStatus, TaskType
from .url_task import URLTask
from .ai_task import AITask
from .configurable_task import ConfigurableTask

__all__ = ['BaseTask', 'TaskStatus', 'TaskType', 'URLTask', 'AITask', 'ConfigurableTask']
