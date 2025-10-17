import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os
from datetime import datetime
import logging
import json  # NEW: Import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_time_series(series_id: str, observation_start: str = None, observation_end: str = None) -> str:
    """
    Grafica una serie de tiempo de FRED con estilo APA.

    Args:
        series_id: ID de la serie de FRED (ej: 'GDP', 'CPIAUCSL', 'UNRATE')
        observation_start: Fecha de inicio (formato: 'YYYY-MM-DD'). Opcional.
        observation_end: Fecha de fin (formato: 'YYYY-MM-DD'). Opcional.

    Returns:
        str: JSON string con rutas de archivos generados
    """

    # Validar API key
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY environment variable is missing")

    fred = Fred(api_key=api_key)

    try:
        # 1. Obtener metadatos de la serie
        series_info = fred.get_series_info(series_id)
        series_title = series_info.get('title', series_id)
        series_units = series_info.get('units', '')
        series_frequency = series_info.get('frequency', '')
        series_seasonal = series_info.get('seasonal_adjustment', '')

        # 2. Obtener datos de observaciones
        df = fred.get_series(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end
        )
        df = pd.Series(df).dropna().reset_index()
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"])

        if df.empty:
            raise ValueError(f"No data available for series {series_id}")

        # 3. Preparar directorios para guardar datos y gráfico
        base_dir = r"C:\Users\agust\Downloads\FRED_Data"
        series_dir = os.path.join(base_dir, series_id)
        series_subdir = os.path.join(series_dir, "series")
        grafico_subdir = os.path.join(series_dir, "grafico")
        os.makedirs(series_subdir, exist_ok=True)
        os.makedirs(grafico_subdir, exist_ok=True)

        # 3.1 Guardar datos en CSV y Excel
        start_date = df["date"].min().strftime("%Y-%m-%d")
        end_date = df["date"].max().strftime("%Y-%m-%d")
        download_date = datetime.now().strftime("%Y%m%d")

        data_filename = f"{series_id}_{start_date}_to_{end_date}_downloaded_{download_date}"
        csv_path = os.path.join(series_subdir, f"{data_filename}.csv")
        xlsx_path = os.path.join(series_subdir, f"{data_filename}.xlsx")

        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)

        logger.info(f"Data saved - CSV: {csv_path}")
        logger.info(f"Data saved - Excel: {xlsx_path}")

        # 4. Configurar estilo APA
        plt.style.use('classic')
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'

        # 5. Crear figura
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        # 6. Graficar datos
        ax.plot(df["date"], df["value"], linewidth=1.5, color='#2E5090')

        # 7. Configurar título y subtítulo
        title = f"{series_title}"
        subtitle_parts = []
        if series_frequency:
            subtitle_parts.append(f"Frequency: {series_frequency}")
        if series_seasonal:
            subtitle_parts.append(f"Seasonal Adj: {series_seasonal}")
        if series_units:
            subtitle_parts.append(f"Units: {series_units}")
        subtitle = ", ".join(subtitle_parts)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        if subtitle:
            ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
                   fontsize=10, ha='center', style='italic')

        # 8. Configurar ejes
        ax.set_xlabel('Date', fontsize=11, fontweight='normal')
        ax.set_ylabel('Value', fontsize=11, fontweight='normal')

        # Formato de fechas en eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')

        # 9. Grid ligero (estilo APA)
        ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)

        # 10. Nota al pie con fuente y fecha
        note = f"Source: Federal Reserve Economic Data (FRED)\nSeries: {series_id} | Period: {start_date} to {end_date}"
        fig.text(0.12, -0.05, note, fontsize=9, style='italic', wrap=True)

        # 11. Ajustar layout
        plt.tight_layout()

        # 12. Guardar gráfico
        filename = f"{series_id}_{start_date}_to_{end_date}_plot_{download_date}.png"
        plot_path = os.path.join(grafico_subdir, filename)

        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Plot saved: {plot_path}")

        # ==================== RETURN JSON (NOT TEXT) ====================
        result = {
            "tool": "plot_fred_series",
            "series_id": series_id,
            "series_title": series_title,
            "plot_path": plot_path,
            "csv_path": csv_path,
            "excel_path": xlsx_path,
            "start_date": start_date,
            "end_date": end_date,
            "message": f"Plot generated successfully for {series_id}"
        }
        
        return json.dumps(result, indent=2)
        # ==================== END ====================



    except Exception as e:
        logger.error(f"Error plotting series {series_id}: {str(e)}")
        
        error_result = {
            "tool": "plot_fred_series",
            "series_id": series_id,
            "error": str(e),
            "plot_path": None,
            "csv_path": None,
            "excel_path": None
        }
        
        return json.dumps(error_result, indent=2)
