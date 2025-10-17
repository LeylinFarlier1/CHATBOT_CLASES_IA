"""
Tool: Fetch FRED series observations (historical data).
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional
from fredapi import Fred
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_series_observations(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None
) -> str:
    """
    Fetches historical observations for a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
        observation_start: Start date in 'YYYY-MM-DD' format. Optional.
        observation_end: End date in 'YYYY-MM-DD' format. Optional.

    Returns:
        JSON with historical data (date, value pairs)
    """
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is missing")

        fred = Fred(api_key)

        # Fetch data
        df = fred.get_series(
            series_id,
            observation_start=observation_start or "1776-07-04",  # FRED start
            observation_end=observation_end
        )

        # Process data
        df = pd.Series(df).dropna().reset_index()
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"])

        observations = df.to_dict("records")

        output = {
            "tool": "fetch_series_observations",
            "series_id": series_id,
            "data": observations,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "observation_start": observation_start or "all",
                "observation_end": observation_end or "latest",
                "total_count": len(observations),
                "date_range": {
                    "start": df["date"].min().isoformat() if not df.empty else None,
                    "end": df["date"].max().isoformat() if not df.empty else None
                }
            }
        }

        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        logger.error(f"Error fetching observations for {series_id}: {e}")
        return json.dumps({
            "error": str(e),
            "series_id": series_id,
            "tool": "fetch_series_observations"
        })
