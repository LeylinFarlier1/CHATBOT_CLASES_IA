"""
Tool: Fetch details for a specific FRED category.
"""
import os
import json
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


def fetch_category_details(category_id: str) -> str:
    """
    Fetches details for a specific FRED category.

    Args:
        category_id: FRED category ID (e.g., '32991' for Money, Banking, & Finance)

    Returns:
        JSON with category details
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        url = "https://api.stlouisfed.org/fred/category"

        params = {
            "category_id": category_id,
            "api_key": api_key,
            "file_type": "json"
        }

        response = requests.get(url, params=params)

        if not response.ok:
            raise ValueError(f"Error fetching category {category_id}: {response.status_code}")

        json_data = response.json()

        output = {
            "tool": "fetch_category_details",
            "category_id": category_id,
            "data": json_data.get("categories", [json_data])[0] if "categories" in json_data else json_data,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "category_id": category_id
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {e}")
        return json.dumps({
            "error": str(e),
            "category_id": category_id,
            "tool": "fetch_category_details"
        })
