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

"""Itinerary management tool.

Stores and retrieves trip logistics — flights, hotels, activities,
and daily schedules — as structured Markdown.
"""

from __future__ import annotations

from google.adk.tools import ToolContext
from app.shared.markdown_store import append_markdown, read_markdown, write_markdown


def save_flight(
    airline: str,
    flight_number: str,
    departure_city: str,
    arrival_city: str,
    departure_datetime: str,
    arrival_datetime: str,
    confirmation_code: str = "Not provided",
    tool_context: ToolContext = None,
) -> dict:
    """Save a flight to the trip itinerary.

    Args:
        airline: The airline name (e.g., 'Delta', 'United').
        flight_number: The flight number (e.g., 'DL1234').
        departure_city: The departure city or airport code.
        arrival_city: The arrival city or airport code.
        departure_datetime: Departure date and time as a string
            (e.g., '2025-08-15 14:30').
        arrival_datetime: Arrival date and time as a string
            (e.g., '2025-08-15 18:45').
        confirmation_code: Booking confirmation code.
        tool_context: The runtime context containing user state.

    Returns:
        A dict confirming the flight was saved.
    """
    user_id = tool_context.state.get("user_id", "default_user") if tool_context else "default_user"

    flight_md = f"""
## ✈️ {airline} {flight_number}

| Field | Details |
|---|---|
| **Route** | {departure_city} to {arrival_city} |
| **Departure** | {departure_datetime} |
| **Arrival** | {arrival_datetime} |
| **Confirmation** | `{confirmation_code}` |

---
"""
    # Check if itinerary exists; if not, create with header
    existing = read_markdown(user_id, "itinerary.md")
    if existing is None:
        header = "# 🌴 Trip Itinerary\n\n# Flights\n"
        write_markdown(user_id, "itinerary.md", header + flight_md)
    else:
        append_markdown(user_id, "itinerary.md", flight_md)

    return {
        "status": "success",
        "message": f"Flight {airline} {flight_number} saved to itinerary.",
    }


def save_hotel(
    hotel_name: str,
    address: str,
    check_in_date: str,
    check_out_date: str,
    confirmation_code: str,
    notes: str,
    tool_context: ToolContext,
) -> dict:
    """Save a hotel reservation to the trip itinerary.

    Args:
        hotel_name: Name of the hotel.
        address: Hotel address.
        check_in_date: Check-in date (e.g., '2025-08-15').
        check_out_date: Check-out date (e.g., '2025-08-20').
        confirmation_code: Booking confirmation code.
        notes: Any additional notes (e.g., 'ocean view room, late checkout').
        tool_context: The runtime context containing user state.

    Returns:
        A dict confirming the hotel was saved.
    """
    user_id = tool_context.state.get("user_id", "default_user")

    hotel_md = f"""
## 🏨 {hotel_name}

| Field | Details |
|---|---|
| **Address** | {address} |
| **Check-in** | {check_in_date} |
| **Check-out** | {check_out_date} |
| **Confirmation** | `{confirmation_code}` |
| **Notes** | {notes} |

---
"""
    existing = read_markdown(user_id, "itinerary.md")
    if existing is None:
        header = "# 🌴 Trip Itinerary\n\n# Hotels\n"
        write_markdown(user_id, "itinerary.md", header + hotel_md)
    elif "# Hotels" not in existing:
        append_markdown(user_id, "itinerary.md", "\n# Hotels\n" + hotel_md)
    else:
        append_markdown(user_id, "itinerary.md", hotel_md)

    return {
        "status": "success",
        "message": f"Hotel {hotel_name} saved to itinerary.",
    }


def save_activity(
    activity_name: str,
    date: str,
    time: str,
    location: str,
    notes: str,
    tool_context: ToolContext,
) -> dict:
    """Save a planned activity or excursion to the trip itinerary.

    Args:
        activity_name: Name of the activity or excursion.
        date: Date of the activity (e.g., '2025-08-16').
        time: Time of the activity (e.g., '10:00 AM').
        location: Location or meeting point.
        notes: Additional details or booking info.
        tool_context: The runtime context containing user state.

    Returns:
        A dict confirming the activity was saved.
    """
    user_id = tool_context.state.get("user_id", "default_user")

    activity_md = f"""
## 🎯 {activity_name}

| Field | Details |
|---|---|
| **Date** | {date} |
| **Time** | {time} |
| **Location** | {location} |
| **Notes** | {notes} |

---
"""
    existing = read_markdown(user_id, "itinerary.md")
    if existing is None:
        header = "# 🌴 Trip Itinerary\n\n# Activities\n"
        write_markdown(user_id, "itinerary.md", header + activity_md)
    elif "# Activities" not in existing:
        append_markdown(user_id, "itinerary.md", "\n# Activities\n" + activity_md)
    else:
        append_markdown(user_id, "itinerary.md", activity_md)

    return {
        "status": "success",
        "message": f"Activity '{activity_name}' saved to itinerary.",
    }


def get_itinerary(tool_context: ToolContext) -> dict:
    """Retrieve the consolidated trip itinerary markdown file.

    Args:
        tool_context: The runtime context containing user state.

    Returns:
        A dict containing status and the full itinerary markdown string.
    """
    user_id = tool_context.state.get("user_id", "default_user")
    
    itinerary_md = read_markdown(user_id, "itinerary.md")
    
    if not itinerary_md:
        return {"status": "not_found", "message": "No itinerary found yet."}
        
    return {
        "status": "success",
        "itinerary_markdown": itinerary_md
    }