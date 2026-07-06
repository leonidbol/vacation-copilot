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

"""Unit tests for vacation-copilot tools.

These validate pure deterministic code correctness (imports, basic return types, 
and file I/O operations) without making actual live LLM calls.
"""

from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock

# Establish an isolated temporary directory configuration before application modules
# execute their top-level imports and parse environment configurations.
TEST_DATA_DIR = tempfile.mkdtemp()
os.environ["VACATION_DATA_DIR"] = TEST_DATA_DIR

from app.shared.markdown_store import (  # noqa: E402
    append_markdown,
    ensure_data_dir,
    list_user_files,
    read_markdown,
    write_markdown,
)
from app.tools.document_parser import (  # noqa: E402
    _detect_document_type,
    parse_travel_document,
)
from app.tools.menu_analyzer import _slugify  # noqa: E402

# ── Markdown Store Tests ──────────────────────────────────────────


class TestMarkdownStore:
    """Validates local filesystem sandbox read, write, and list operations."""

    def test_ensure_data_dir_creates_directory(self) -> None:
        """Verify that user-scoped directories are provisioned on demand."""
        user_dir = ensure_data_dir("test_user_1")
        assert user_dir.exists()
        assert user_dir.is_dir()

    def test_write_and_read_markdown(self) -> None:
        """Verify markdown writing persists content identical to retrieval forms."""
        write_markdown("test_user_2", "test.md", "# Hello World")
        content = read_markdown("test_user_2", "test.md")
        assert content == "# Hello World"

    def test_read_nonexistent_returns_none(self) -> None:
        """Ensure missing files do not raise exceptions and return cleanly as None."""
        result = read_markdown("nonexistent_user", "nope.md")
        assert result is None

    def test_append_markdown(self) -> None:
        """Verify file mutation appends rather than overwriting existing blocks."""
        write_markdown("test_user_3", "append.md", "# Start\n")
        append_markdown("test_user_3", "append.md", "## Added Section\n")
        content = read_markdown("test_user_3", "append.md")
        assert content is not None
        assert "# Start" in content
        assert "## Added Section" in content

    def test_list_user_files(self) -> None:
        """Verify directory indexes return all discrete files mapped to a user space."""
        write_markdown("test_user_4", "file1.md", "content1")
        write_markdown("test_user_4", "file2.md", "content2")
        files = list_user_files("test_user_4")
        assert "file1.md" in files
        assert "file2.md" in files


# ── Document Parser Tests ─────────────────────────────────────────


class TestDocumentParser:
    """Validates structural routing logic based on regex document classification."""

    def test_detect_flight_document(self) -> None:
        """Verify flight matching syntax flags appropriately."""
        assert _detect_document_type("Your flight DL1234 departs at 3pm") == "flight"

    def test_detect_hotel_document(self) -> None:
        """Verify lodging parameters flag appropriately."""
        assert _detect_document_type("Hotel reservation: check-in Aug 15") == "hotel"

    def test_detect_restaurant_menu(self) -> None:
        """Verify culinary item structures map cleanly to menu contexts."""
        assert _detect_document_type("Appetizer: Bruschetta $12") == "restaurant_menu"

    def test_detect_activity(self) -> None:
        """Verify excursion patterns catch cleanly."""
        assert _detect_document_type("Museum tour ticket for Aug 16") == "activity"

    def test_detect_general(self) -> None:
        """Verify fallback triggers safely for standard unstructured strings."""
        assert _detect_document_type("Some random travel info") == "general_travel"

    def test_parse_travel_document_returns_dict(self) -> None:
        """Verify tool parsing initializes standardized schema metadata structures."""
        mock_ctx = MagicMock()
        mock_ctx.state = {}
        result = parse_travel_document("Flight DL1234 departing LAX", mock_ctx)
        assert result["status"] == "success"
        assert result["document_type"] == "flight"
        assert "extracted_data" in result


# ── Menu Analyzer Tests ───────────────────────────────────────────


class TestMenuAnalyzer:
    """Validates internal utility helpers driving item lookups."""

    def test_slugify(self) -> None:
        """Verify special character normalization and casing patterns."""
        assert _slugify("La Bella Italia!") == "la_bella_italia"
        assert _slugify("Café du Monde") == "café_du_monde"

    def test_slugify_max_length(self) -> None:
        """Verify that slug boundaries strictly truncate to avoid long filename limits."""
        long_name = "A" * 100
        assert len(_slugify(long_name)) <= 50