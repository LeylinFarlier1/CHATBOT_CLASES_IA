"""
Tool: Fetch FRED series metadata.
"""
import os
import json
import logging
from datetime import datetime
from fredapi import Fred

logger = logging.getLogger(__name__)


def fetch_series_metadata(series_id: str) -> str:
    """
    Fetches metadata for a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')

    Returns:
        JSON with series metadata (title, units, frequency, seasonal adjustment, etc.)
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        fred = Fred(api_key)
        series_info = fred.get_series_info(series_id)

        # Extraer solo los campos relevantes (evitar objetos pandas internos)
        data = {
            "id": str(series_info.get("id", "")),
            "title": str(series_info.get("title", "")),
            "observation_start": str(series_info.get("observation_start", "")),
            "observation_end": str(series_info.get("observation_end", "")),
            "frequency": str(series_info.get("frequency", "")),
            "frequency_short": str(series_info.get("frequency_short", "")),
            "units": str(series_info.get("units", "")),
            "units_short": str(series_info.get("units_short", "")),
            "seasonal_adjustment": str(series_info.get("seasonal_adjustment", "")),
            "seasonal_adjustment_short": str(series_info.get("seasonal_adjustment_short", "")),
            "last_updated": str(series_info.get("last_updated", "")),
            "popularity": str(series_info.get("popularity", "")),
            "notes": str(series_info.get("notes", ""))
        }

        output = {
            "tool": "fetch_series_metadata",
            "series_id": series_id,
            "data": data,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "series_id": series_id
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching series metadata for {series_id}: {e}")
        return json.dumps({
            "error": str(e),
            "series_id": series_id,
            "tool": "fetch_series_metadata"
        })
