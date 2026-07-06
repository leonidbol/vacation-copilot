# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Markdown-first data storage utilities.

All vacation data is persisted as clean, human-readable Markdown files.
This module provides read/write helpers that the agent tools use to
store and retrieve structured travel information.
"""

from __future__ import annotations

import os
from pathlib import Path

# Default data directory (can be overridden via env)
_env_dir = os.environ.get("VACATION_DATA_DIR")
DATA_DIR = Path(_env_dir) if _env_dir else Path(__file__).resolve().parent.parent.parent / "data"


def ensure_data_dir(user_id: str) -> Path:
    """Create and return the user-specific data directory."""
    user_dir = DATA_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def write_markdown(user_id: str, filename: str, content: str) -> str:
    """Write content to a Markdown file in the user's data directory.

    Args:
        user_id: The user identifier.
        filename: Name of the markdown file (e.g. 'profile.md').
        content: The markdown content to write.

    Returns:
        The absolute path of the written file.
    """
    user_dir = ensure_data_dir(user_id)
    filepath = user_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def read_markdown(user_id: str, filename: str) -> str | None:
    """Read a Markdown file from the user's data directory.

    Args:
        user_id: The user identifier.
        filename: Name of the markdown file.

    Returns:
        The file contents as a string, or None if not found.
    """
    filepath = ensure_data_dir(user_id) / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def append_markdown(user_id: str, filename: str, content: str) -> str:
    """Append content to a Markdown file, inserting a newline if needed.

    Args:
        user_id: The user identifier.
        filename: Name of the markdown file.
        content: The markdown content to append.

    Returns:
        The absolute path of the modified file.
    """
    user_dir = ensure_data_dir(user_id)
    filepath = user_dir / filename
    
    needs_newline = False
    if filepath.exists() and filepath.stat().st_size > 0:
        with open(filepath, "rb") as f:
            f.seek(-1, os.SEEK_END)
            needs_newline = f.read(1) != b"\n"

    with open(filepath, "a", encoding="utf-8") as f:
        if needs_newline and not content.startswith("\n"):
            f.write("\n")
        f.write(content)
    return str(filepath)


def list_user_files(user_id: str) -> list[str]:
    """List all markdown files for a user.

    Args:
        user_id: The user identifier.

    Returns:
        List of filenames in the user's data directory.
    """
    user_dir = ensure_data_dir(user_id)
    return [f.name for f in user_dir.iterdir() if f.is_file() and f.suffix == ".md"]