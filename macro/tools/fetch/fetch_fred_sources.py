"""
Tool: Fetch list of all FRED data sources.
"""
import os
import json
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


def fetch_fred_sources() -> str:
    """
    Fetches list of all FRED data sources.

    Returns:
        JSON with list of data sources
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        url = "https://api.stlouisfed.org/fred/sources"

        params = {
            "api_key": api_key,
            "file_type": "json"
        }

        response = requests.get(url, params=params)

        if not response.ok:
            raise ValueError(f"Error fetching sources: {response.status_code}")

        json_data = response.json()
        sources = json_data.get("sources", [])

        output = {
            "tool": "fetch_fred_sources",
            "data": sources,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "total_count": len(sources)
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching sources list: {e}")
        return json.dumps({
            "error": str(e),
            "tool": "fetch_fred_sources"
        })
