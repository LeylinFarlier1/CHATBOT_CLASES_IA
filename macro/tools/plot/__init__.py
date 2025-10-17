"""
Tools de visualización y gráficos de datos macroeconómicos.

Este módulo contiene herramientas para crear gráficos:
- Series temporales simples
- Comparaciones de doble eje
- Análisis de diferenciación
- Gráficos desde datasets construidos
"""

from .plot_fred_series import plot_time_series
from .plot_dual_axis import plot_dual_axis_comparison
from .analyze_differencing import analyze_differencing
from .plot_from_dataset import plot_from_dataset

__all__ = [
    'plot_time_series',
    'plot_dual_axis_comparison',
    'analyze_differencing',
    'plot_from_dataset',
]
