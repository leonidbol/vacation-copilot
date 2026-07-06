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

"""Menu analysis and dietary matching tool.

Parses restaurant menus and cross-references dishes with the
traveler's profile to surface optimized dining choices.
"""

from __future__ import annotations

import re
from google.adk.tools import ToolContext
from app.shared.markdown_store import read_markdown, write_markdown


def parse_and_match_menu(
    restaurant_name: str, menu_text: str, tool_context: ToolContext
) -> dict:
    """Parse a restaurant menu and match dishes to traveler preferences.

    Takes raw menu text and cross-references each dish against the user's
    dietary restrictions, cuisine preferences, and macro goals to produce
    personalized recommendations. If the volatile session cache is empty,
    it re-hydrates preferences by reading the disk-persisted profile.

    Args:
        restaurant_name: Name of the restaurant.
        menu_text: The raw menu content — can be pasted text,
            OCR output from a photo, or a structured listing.
        tool_context: The ADK runner context containing session state.

    Returns:
        A dict with the parsed menu, profile match results,
        and an instruction prompt for the orchestrating agent.
    """
    user_id = tool_context.state.get("user_id", "default_user")

    # 1. Attempt to grab profile fields from active session memory
    dietary = tool_context.state.get("user:dietary_restrictions")
    cuisine_prefs = tool_context.state.get("user:cuisine_preferences")
    macro_goals = tool_context.state.get("user:macro_goals")
    travel_style = tool_context.state.get("user:travel_style")

    # 2. State Re-hydration: If session memory is bare but profile.md exists, parse disk
    profile_md = read_markdown(user_id, "profile.md")
    if profile_md and not (dietary or cuisine_prefs or macro_goals):
        dietary = _extract_md_section(profile_md, "Dietary Restrictions")
        cuisine_prefs = _extract_md_section(profile_md, "Cuisine Preferences")
        macro_goals = _extract_md_section(profile_md, "Nutritional / Macro Goals")
        travel_style = _extract_md_section(profile_md, "Travel Style")

        # Re-populate session state so future tool turns bypass disk reads
        tool_context.state["user:dietary_restrictions"] = dietary
        tool_context.state["user:cuisine_preferences"] = cuisine_prefs
        tool_context.state["user:macro_goals"] = macro_goals
        tool_context.state["user:travel_style"] = travel_style

    # 3. Establish clean structural fallbacks if data fields are completely missing
    dietary = dietary or "None specified"
    cuisine_prefs = cuisine_prefs or "None specified"
    macro_goals = macro_goals or "None specified"
    travel_style = travel_style or "None specified"

    # 4. Record the raw menu audit trail to disk for historical logging
    menu_md = f"""# 🍽️ {restaurant_name} — Menu

{menu_text}

---
_Analyzed for traveler profile matching._
"""
    write_markdown(user_id, f"menu_{_slugify(restaurant_name)}.md", menu_md)

    return {
        "status": "success",
        "restaurant_name": restaurant_name,
        "menu_content": menu_text,
        "traveler_profile": {
            "dietary_restrictions": dietary,
            "cuisine_preferences": cuisine_prefs,
            "macro_goals": macro_goals,
            "travel_style": travel_style,
        },
        "profile_available": bool(profile_md),
        "instruction": (
            f"Analyze the menu from {restaurant_name}. "
            "For each dish, evaluate: "
            "1) Does it satisfy dietary restrictions? "
            "2) Does it align with cuisine preferences? "
            "3) Does it fit macro goals? "
            "Rank the top 3-5 recommended dishes with reasoning. "
            "Flag any dishes that violate dietary restrictions. "
            "If the menu is in a foreign language, translate dish names "
            "and provide brief descriptions."
        ),
    }


def save_menu_recommendations(
    restaurant_name: str, recommendations_markdown: str, tool_context: ToolContext
) -> dict:
    """Save the agent's menu recommendations for future reference.

    Args:
        restaurant_name: Name of the restaurant.
        recommendations_markdown: The formatted recommendations
            as markdown text.
        tool_context: The ADK runner context containing session state.

    Returns:
        A dict confirming the recommendations were saved.
    """
    user_id = tool_context.state.get("user_id", "default_user")

    filepath = write_markdown(
        user_id,
        f"recs_{_slugify(restaurant_name)}.md",
        f"# 🌟 Recommendations — {restaurant_name}\n\n{recommendations_markdown}",
    )
    return {
        "status": "success",
        "message": f"Recommendations saved to {filepath}",
    }


def _slugify(text: str) -> str:
    """Create a clean, filename-safe slug from text without messy repeating underscores."""
    raw_slug = "".join(c if c.isalnum() else "_" for c in text.lower())
    clean_slug = re.sub(r'_{2,}', '_', raw_slug)
    return clean_slug.strip("_")[:50]


def _extract_md_section(md_text: str, section_title: str) -> str:
    """Parse out specific section bullet points from markdown text and convert back to CSV."""
    # Supporting cross-platform line breaks (\r\n and \n)
    pattern = rf"##\s*{re.escape(section_title)}\r?\n(.*?)(?=\r?\n##|\Z)"
    match = re.search(pattern, md_text, re.DOTALL)
    if not match:
        return ""

    # Isolate lines starting with markdown bullets (-)
    bullets = re.findall(r"-\s*(.*)", match.group(1))
    cleaned_items = []
    for item in bullets:
        item_stripped = item.strip()
        # Drop markdown structural placeholders or unassigned indicators
        if item_stripped and not item_stripped.startswith(("_Not specified_", "None")):
            cleaned_items.append(item_stripped)

    return ", ".join(cleaned_items) if cleaned_items else ""