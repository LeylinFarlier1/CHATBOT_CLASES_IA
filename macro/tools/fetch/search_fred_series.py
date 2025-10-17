"""
Tool: Search FRED series by text.
"""
import os
import json
import logging
import time
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


def search_fred_series(search_text: str, limit: int = 50) -> str:
    """
    Searches FRED series by text query.

    Args:
        search_text: Search query (e.g., 'unemployment', 'inflation', 'GDP')
        limit: Maximum number of results to return (default: 50)

    Returns:
        JSON with search results ordered by popularity
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        url = "https://api.stlouisfed.org/fred/series/search"

        params = {
            "search_text": search_text,
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": "popularity",
            "sort_order": "desc"
        }

        response = requests.get(url, params=params)

        if response.status_code == 429:
            time.sleep(1)
            response = requests.get(url, params=params)

        if not response.ok:
            raise ValueError(f"Error fetching search results: {response.status_code}")

        json_data = response.json()
        results = json_data.get("seriess", [])

        output = {
            "tool": "search_fred_series",
            "search_text": search_text,
            "data": results,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "search_text": search_text,
                "total_count": json_data.get("count", len(results)),
                "returned_count": len(results)
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error searching series with text '{search_text}': {e}")
        return json.dumps({
            "error": str(e),
            "search_text": search_text,
            "tool": "search_fred_series"
        })
