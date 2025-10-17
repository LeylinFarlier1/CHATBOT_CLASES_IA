"""
Tool: Fetch details for a specific FRED release.
"""
import os
import json
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


def fetch_release_details(release_id: str) -> str:
    """
    Fetches details for a specific FRED release.

    Args:
        release_id: FRED release ID (e.g., '53' for Gross Domestic Product)

    Returns:
        JSON with release details
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        url = "https://api.stlouisfed.org/fred/release"

        params = {
            "release_id": release_id,
            "api_key": api_key,
            "file_type": "json"
        }

        response = requests.get(url, params=params)

        if not response.ok:
            raise ValueError(f"Error fetching release {release_id}: {response.status_code}")

        json_data = response.json()

        output = {
            "tool": "fetch_release_details",
            "release_id": release_id,
            "data": json_data.get("releases", [json_data])[0] if "releases" in json_data else json_data,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "release_id": release_id
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching release {release_id}: {e}")
        return json.dumps({
            "error": str(e),
            "release_id": release_id,
            "tool": "fetch_release_details"
        })
