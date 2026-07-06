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

"""User profile management tool.

Manages the traveler's profile including dietary restrictions,
cuisine preferences, macro goals, and travel style.
"""

from __future__ import annotations

from google.adk.tools import ToolContext
from app.shared.markdown_store import read_markdown, write_markdown


def save_user_profile(
    tool_context: ToolContext,
    dietary_restrictions: str = "",
    cuisine_preferences: str = "",
    macro_goals: str = "",
    travel_style: str = "",
) -> dict:
    """Save or update the traveler's personal profile preferences.

    Args:
        tool_context: The ADK runner context containing session state.
        dietary_restrictions: Comma-separated dietary restrictions
            (e.g., 'gluten-free, no shellfish, vegetarian').
        cuisine_preferences: Comma-separated preferred cuisines or
            food interests (e.g., 'authentic local, seafood, street food').
        macro_goals: Nutritional goals or macro preferences
            (e.g., 'high protein, low carb, under 600 cal per meal').
        travel_style: Travel style preferences
            (e.g., 'adventurous eater, budget-friendly, luxury').

    Returns:
        A dict confirming the profile was saved.
    """
    user_id = tool_context.state.get("user_id", "default_user")

    md_content = f"""# Traveler Profile

## Dietary Restrictions
{_to_bullet_list(dietary_restrictions)}

## Cuisine Preferences
{_to_bullet_list(cuisine_preferences)}

## Nutritional / Macro Goals
{_to_bullet_list(macro_goals)}

## Travel Style
{_to_bullet_list(travel_style)}
"""
    filepath = write_markdown(user_id, "profile.md", md_content)

    # Also store in session state for quick access across tool runs
    tool_context.state["user:dietary_restrictions"] = dietary_restrictions
    tool_context.state["user:cuisine_preferences"] = cuisine_preferences
    tool_context.state["user:macro_goals"] = macro_goals
    tool_context.state["user:travel_style"] = travel_style

    return {
        "status": "success",
        "message": f"Profile saved to {filepath}",
        "profile_summary": {
            "dietary_restrictions": dietary_restrictions,
            "cuisine_preferences": cuisine_preferences,
            "macro_goals": macro_goals,
            "travel_style": travel_style,
        },
    }


def get_user_profile(tool_context: ToolContext) -> dict:
    """Retrieve the traveler's saved profile markdown from disk.

    Args:
        tool_context: The ADK runner context containing session state.

    Returns:
        A dict containing the profile data or a message if no profile exists.
    """
    user_id = tool_context.state.get("user_id", "default_user")
    content = read_markdown(user_id, "profile.md")

    if content:
        return {"status": "success", "profile_markdown": content}
    return {"status": "not_found", "message": "No profile found. Let's set one up!"}


def _to_bullet_list(csv_string: str | None) -> str:
    """Convert a comma-separated string to a markdown bullet list safely."""
    if not csv_string or not isinstance(csv_string, str):
        return "- _Not specified_"
        
    items = [item.strip() for item in csv_string.split(",") if item.strip()]
    if not items:
        return "- _Not specified_"
    return "\n".join(f"- {item}" for item in items)