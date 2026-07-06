# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

class ExtractedTravelData(BaseModel):
    # Removed model_config = ConfigDict(extra="forbid") to comply with Developer API JSON Schema limitations
    category: str = Field(description="flight, hotel, activity, or general")
    confidence_score: float
    details: str = Field(description="Extracted key-value pairs formatted as a stringified JSON block (e.g., flight_number, check_in_date, confirmation_code)")


def _detect_document_type(text: str) -> str:
    """Fallback string-matching heuristic to categorize documents if the API fails."""
    lower_text = text.lower()
    if any(keyword in lower_text for keyword in ["flight", "airline", "boarding", "terminal", "pnr"]):
        return "flight"
    if any(keyword in lower_text for keyword in ["hotel", "check-in", "stay", "room", "accommodation", "resort"]):
        return "hotel"
    if any(keyword in lower_text for keyword in ["activity", "tour", "ticket", "reservation", "excursion"]):
        return "activity"
    # Detect restaurant menu documents (appetizer, price symbols, etc.)
    if any(keyword in lower_text for keyword in ["appetizer", "entree", "main course", "dessert", "menu"] ) or "$" in text:
        return "restaurant_menu"
    # Fallback for generic travel text
    return "general_travel"


def parse_travel_document(raw_text: str, tool_context: ToolContext) -> dict:
    """Parse unstructured travel text and extract structured information immediately."""
    
    # Initialize the standard Google GenAI client
    ai = genai.Client()
    
    prompt = f"Extract all structured travel parameters out of the following raw text:\n\n{raw_text}"
    
    try:
        response = ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedTravelData,
                temperature=0.1,
            )
        )
        
        # Safely parse the structured JSON text string into a native dict
        extracted_dict = json.loads(response.text)
        
        # If the model returned details as an escaped string representation of a JSON object, safely unpack it
        if isinstance(extracted_dict.get("details"), str):
            try:
                extracted_dict["details"] = json.loads(extracted_dict["details"])
            except Exception:
                pass
        
        return {
            "status": "success",
            "document_type": extracted_dict.get("category", "general"), # Added to satisfy the unit test expectation
            "extracted_data": extracted_dict
        }
    except Exception as e:
        logger.error("Failed structured content generation via Gemini API, executing fallback: %s", e, exc_info=True)
        # Fallback to the heuristic if the network call fails
        return {
            "status": "fallback",
            "document_type": _detect_document_type(raw_text),
            "raw_content": raw_text
        }