# app/server_mcp.py
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import json
import logging

# === Importar herramientas ===
import sys
# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# === Importar tools organizados por categoría ===

# Tools de consulta/obtención de datos (fetch)
from tools.fetch import (
    fetch_series_metadata,
    fetch_series_observations,
    search_fred_series,
    fetch_fred_releases,
    fetch_release_details,
    fetch_category_details,
    fetch_fred_sources,
)

# Tools de visualización (plot)
from tools.plot import (
    plot_time_series,
    plot_dual_axis_comparison,
    analyze_differencing,
    plot_from_dataset,
)

# Tools de construcción de datasets (build/ETL)
from tools.build import build_fred_dataset

# === Importar resources (datos read-only) ===
from resources.datasets import list_recent_datasets, find_dataset_with_columns

# === Configuración base ===
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("macro-chatbot")

# =============================================
# ====   REGISTRO DE TOOLS & RESOURCES   ======
# =============================================

@mcp.tool()
def get_economic_indicator(country: str, indicator: str):
    """Obtiene un indicador económico de ejemplo para un país."""
    return {
        "country": country,
        "indicator": indicator,
        "value": 0.0,
        "year": 2024,
        "unit": "TBD"
    }


@mcp.tool()
def compare_economies(country1: str, country2: str):
    """Compara indicadores económicos básicos entre dos países."""
    return {
        "country1": country1,
        "country2": country2,
        "comparison": "Datos de comparación pendientes de implementación"
    }


@mcp.tool()
def plot_fred_series_tool(series_id: str, observation_start: str = None, observation_end: str = None) -> str:
    """
    MCP Tool: Creates a time series plot of FRED data with APA style formatting.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'CPIAUCSL', 'UNRATE')
        observation_start: Start date in 'YYYY-MM-DD' format. Optional.
        observation_end: End date in 'YYYY-MM-DD' format. Optional.

    Returns:
        Message with the path to the saved plot file
    """
    try:
        result = plot_time_series(series_id, observation_start, observation_end)
        return json.dumps({
            "status": "success",
            "message": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.exception("Error running plot_fred_series_tool")
    return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


@mcp.tool()
def analyze_differencing_tool(series_id: str, observation_start: str = None, observation_end: str = None) -> str:
    """
    MCP Tool: Analyzes time series differencing and stationarity with Augmented Dickey-Fuller test.

    Calculates and visualizes:
    - Original series (Xt)
    - First difference (ΔXt = Xt - Xt-1)
    - Second difference (Δ²Xt = Xt - 2*Xt-1 + Xt-2)
    - ADF test results for each series

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'CPIAUCSL', 'UNRATE')
        observation_start: Start date in 'YYYY-MM-DD' format. Optional.
        observation_end: End date in 'YYYY-MM-DD' format. Optional.

    Returns:
        Message with paths to saved files and ADF test results
    """
    return analyze_differencing(series_id, observation_start, observation_end)


@mcp.tool()
def plot_dual_axis_tool(
    series_id_left: str,
    series_id_right: str,
    observation_start: str = None,
    observation_end: str = None,
    left_color: str = "#2E5090",
    right_color: str = "#C1272D"
) -> str:
    """
    MCP Tool: Compares two FRED series on a dual-axis plot with APA style formatting.

    Creates a professional comparison chart with:
    - Left Y-axis for first series
    - Right Y-axis for second series
    - Different colors for each series
    - Synchronized X-axis (dates)
    - Combined legend

    Args:
        series_id_left: FRED series ID for left Y-axis (e.g., 'UNRATE')
        series_id_right: FRED series ID for right Y-axis (e.g., 'CPIAUCSL')
        observation_start: Start date in 'YYYY-MM-DD' format. Optional.
        observation_end: End date in 'YYYY-MM-DD' format. Optional.
        left_color: Color for left series (default: blue '#2E5090')
        right_color: Color for right series (default: red '#C1272D')

    Returns:
        Message with paths to saved plot and data files
    """
    return plot_dual_axis_comparison(
        series_id_left,
        series_id_right,
        observation_start,
        observation_end,
        left_color,
        right_color
    )


@mcp.tool()
def build_fred_dataset_tool(
    series_list: list,
    transformations: dict = None,
    observation_start: str = None,
    observation_end: str = None,
    merge_strategy: str = "inner"
) -> str:
    """
    MCP Tool: Builds a unified macroeconomic dataset from multiple FRED series (ETL pipeline).

    This is the "dataset constructor" that acts as middleware between data extraction and visualization:

    📥 EXTRACT: Downloads multiple FRED series
    🔄 TRANSFORM: Applies transformations (YoY, QoQ, differences, logs, etc.)
    💾 LOAD: Saves unified dataset with synchronized dates

    Benefits:
    - Reusability: No need to recalculate transformations every time
    - Scalability: Build datasets with 5, 10, or 50 series at once
    - Traceability: Each dataset saved with metadata (dates, transformations, series info)
    - Interoperability: Export to CSV/Excel for use in Stata, R, Python, etc.

    Available transformations:
    - 'none': No transformation (raw data)
    - 'YoY': Year-over-Year % change (12 periods)
    - 'QoQ': Quarter-over-Quarter % change (3 periods)
    - 'MoM': Month-over-Month % change (1 period)
    - 'diff': First difference
    - 'pct_change': Simple percentage change
    - 'log': Natural logarithm
    - 'log_diff': Log difference (approximate % change)

    Args:
        series_list: List of FRED series IDs (e.g., ['UNRATE', 'CPIAUCSL', 'GDP'])
        transformations: Dict mapping series_id to transformation type
                        Example: {'CPIAUCSL': 'YoY', 'GDP': 'QoQ', 'UNRATE': 'none'}
                        If not specified, uses raw data for all series
        observation_start: Start date in 'YYYY-MM-DD' format. Optional.
        observation_end: End date in 'YYYY-MM-DD' format. Optional.
        merge_strategy: Merge strategy for combining series ('inner', 'outer', 'left', 'right')
                       Default: 'inner' (only common dates)

    Returns:
        Summary message with dataset info and file paths (CSV, Excel, metadata JSON)

    Example usage:
        Build a dataset with unemployment, inflation (YoY), and GDP growth (QoQ):
        build_fred_dataset_tool(
            series_list=['UNRATE', 'CPIAUCSL', 'GDP'],
            transformations={'CPIAUCSL': 'YoY', 'GDP': 'QoQ'},
            observation_start='2000-01-01'
        )
    """
    return build_fred_dataset(
        series_list,
        transformations,
        observation_start,
        observation_end,
        merge_strategy
    )


@mcp.tool()
def plot_from_dataset_tool(
    column_left: str,
    column_right: str,
    dataset_path: str = None,
    left_color: str = "#2E5090",
    right_color: str = "#C1272D"
) -> str:
    """
    MCP Tool: Plots two columns from a previously built FRED dataset (closes the ETL cycle).

    This tool completes the data pipeline workflow:
    1. build_fred_dataset_tool → creates dataset with transformations
    2. plot_from_dataset_tool → plots columns from dataset without recalculating

    Key advantages:
    - Uses pre-calculated transformations (YoY, QoQ, etc.) from the dataset
    - No need to re-download data from FRED
    - Maintains consistency with dataset transformations
    - Auto-detects latest dataset if path not specified
    - Reads metadata for proper labeling

    Workflow example:
        Step 1: Build dataset
        build_fred_dataset_tool(
            series_list=['UNRATE', 'CPIAUCSL', 'GDP'],
            transformations={'CPIAUCSL': 'YoY', 'GDP': 'QoQ'}
        )
        → Creates dataset with columns: date, UNRATE, CPIAUCSL_YoY, GDP_QoQ

        Step 2: Plot from dataset
        plot_from_dataset_tool(
            column_left='UNRATE',
            column_right='CPIAUCSL_YoY'
        )
        → Plots using transformed data from CSV (no recalculation)

    Args:
        column_left: Column name for left Y-axis (e.g., 'UNRATE', 'CPIAUCSL_YoY')
        column_right: Column name for right Y-axis (e.g., 'GDP_QoQ', 'FEDFUNDS')
        dataset_path: Path to dataset CSV file. If None, uses most recently created dataset.
        left_color: Color for left series (default: blue '#2E5090')
        right_color: Color for right series (default: red '#C1272D')

    Returns:
        Message with path to saved plot and dataset info

    Notes:
        - Column names should match those in the dataset (including transformation suffixes like '_YoY')
        - Automatically detects if same scale or dual axis based on units
        - Saves plots in 'plots' subdirectory within dataset folder
    """
    return plot_from_dataset(
        column_left,
        column_right,
        dataset_path,
        left_color,
        right_color
    )


@mcp.resource("fred://datasets/recent")
def get_recent_datasets_resource() -> str:
    """
    MCP Resource: Lists the most recently created FRED datasets (read-only).

    CRITICAL: This resource solves the MCP client's limited context issue!

    Resources vs Tools:
        - Resources: Read-only data that Claude can access automatically
        - Tools: Actions that modify state or require explicit calls

    Problem this solves:
        User: "Build dataset with UNRATE and CPIAUCSL (YoY)"
        Claude: *builds dataset* ✅
        [CONTEXT LOST]
        User: "Plot UNRATE vs CPIAUCSL_YoY"
        Claude: *can now see available datasets via this resource*
                *uses plot_from_dataset_tool correctly* ✅

    The resource provides automatic visibility of:
        - Dataset names
        - Creation dates
        - Date ranges (observation periods)
        - Available columns (INCLUDING transformation suffixes like _YoY, _QoQ)
        - Applied transformations
        - Full paths to CSV files

    Claude should check this resource when:
        1. User mentions column names with transformation suffixes
        2. User says "plot from dataset" without specifying which one
        3. User references data that might exist in a built dataset

    Returns:
        Formatted list of the 10 most recent FRED datasets with full metadata

    Example output:
        📂 DATASETS RECIENTES (últimos 10)

        1. FRED_dataset_UNRATE_CPIAUCSL
           📅 Creado: 2025-10-11 19:30:15
           📊 Período: 1948-01-01 a 2025-08-01
           🔹 Columnas: UNRATE, CPIAUCSL_YoY
           🔄 Transformaciones: CPIAUCSL → YoY
           📍 Path: C:/Users/.../dataset.csv

        2. FRED_dataset_GDP_FEDFUNDS
           ...
    """
    return list_recent_datasets(limit=10)


# =============================================
# ====     FRED API TOOLS (READ-ONLY) ========
# =============================================

@mcp.tool()
def fetch_series_metadata_tool(series_id: str) -> str:
    """
    Fetches metadata for a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')

    Returns:
        JSON with series metadata (title, units, frequency, seasonal adjustment, etc.)
    """
    return fetch_series_metadata(series_id)


@mcp.tool()
def fetch_series_observations_tool(
    series_id: str,
    observation_start: str = None,
    observation_end: str = None
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
    return fetch_series_observations(series_id, observation_start, observation_end)


@mcp.tool()
def search_fred_series_tool(search_text: str, limit: int = 50) -> str:
    """
    Searches FRED series by text query.

    Args:
        search_text: Search query (e.g., 'unemployment', 'inflation', 'GDP')
        limit: Maximum number of results to return (default: 50)

    Returns:
        JSON with search results ordered by popularity
    """
    return search_fred_series(search_text, limit)


@mcp.tool()
def fetch_fred_releases_tool() -> str:
    """
    Fetches list of all FRED releases.

    Returns:
        JSON with list of available FRED releases
    """
    return fetch_fred_releases()


@mcp.tool()
def fetch_release_details_tool(release_id: str) -> str:
    """
    Fetches details for a specific FRED release.

    Args:
        release_id: FRED release ID (e.g., '53' for Gross Domestic Product)

    Returns:
        JSON with release details
    """
    return fetch_release_details(release_id)


@mcp.tool()
def fetch_category_details_tool(category_id: str) -> str:
    """
    Fetches details for a specific FRED category.

    Args:
        category_id: FRED category ID (e.g., '32991' for Money, Banking, & Finance)

    Returns:
        JSON with category details
    """
    return fetch_category_details(category_id)


@mcp.tool()
def fetch_fred_sources_tool() -> str:
    """
    Fetches list of all FRED data sources.

    Returns:
        JSON with list of data sources
    """
    return fetch_fred_sources()

# === Ejecutar el MCP ===
if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor MCP 'macro-chatbot'...")
    mcp.run()
