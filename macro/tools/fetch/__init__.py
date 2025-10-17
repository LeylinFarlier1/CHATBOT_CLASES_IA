"""
Tools de consulta/obtención de datos de FRED API.

Este módulo contiene herramientas para obtener información de la API de FRED:
- Metadatos de series
- Observaciones históricas
- Búsqueda de series
- Información de releases, categorías y fuentes
"""

from .fetch_series_metadata import fetch_series_metadata
from .fetch_series_observations import fetch_series_observations
from .search_fred_series import search_fred_series
from .fetch_fred_releases import fetch_fred_releases
from .fetch_release_details import fetch_release_details
from .fetch_category_details import fetch_category_details
from .fetch_fred_sources import fetch_fred_sources

__all__ = [
    'fetch_series_metadata',
    'fetch_series_observations',
    'search_fred_series',
    'fetch_fred_releases',
    'fetch_release_details',
    'fetch_category_details',
    'fetch_fred_sources',
]
