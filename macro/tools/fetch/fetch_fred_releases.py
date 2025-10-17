"""
Tool: Fetch list of all FRED releases.
"""
import os
import json
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


def fetch_fred_releases() -> str:
    """
    Fetches list of all FRED releases.

    Returns:
        JSON with list of available FRED releases
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        url = "https://api.stlouisfed.org/fred/releases"

        params = {
            "api_key": api_key,
            "file_type": "json"
        }

        response = requests.get(url, params=params)

        if not response.ok:
            raise ValueError(f"Error fetching releases: {response.status_code}")

        json_data = response.json()
        releases = json_data.get("releases", [])

        output = {
            "tool": "fetch_fred_releases",
            "data": releases,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "total_count": len(releases)
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching releases list: {e}")
        return json.dumps({
            "error": str(e),
            "tool": "fetch_fred_releases"
        })
