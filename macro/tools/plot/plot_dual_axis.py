import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os
from datetime import datetime
import logging
import json  # Add this if not present

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_dual_axis_comparison(
    series_id_left: str,
    series_id_right: str,
    observation_start: str = None,
    observation_end: str = None,
    left_color: str = "#2E5090",
    right_color: str = "#C1272D"
) -> str:
    """
    Compara dos series de FRED en un gráfico con doble eje Y (estilo APA).

    Args:
        series_id_left: ID de la serie para el eje Y izquierdo (ej: 'UNRATE')
        series_id_right: ID de la serie para el eje Y derecho (ej: 'CPIAUCSL')
        observation_start: Fecha de inicio (formato: 'YYYY-MM-DD'). Opcional.
        observation_end: Fecha de fin (formato: 'YYYY-MM-DD'). Opcional.
        left_color: Color para la serie izquierda (default: azul)
        right_color: Color para la serie derecha (default: rojo)

    Returns:
        str: Ruta del gráfico guardado y archivos de datos
    """

    # Validar API key
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY environment variable is missing")

    fred = Fred(api_key=api_key)

    try:
        # 1. Obtener metadatos de ambas series
        series_info_left = fred.get_series_info(series_id_left)
        series_info_right = fred.get_series_info(series_id_right)

        series_title_left = series_info_left.get('title', series_id_left)
        series_title_right = series_info_right.get('title', series_id_right)

        series_units_left = series_info_left.get('units', '')
        series_units_right = series_info_right.get('units', '')

        # 2. Obtener datos de ambas series
        df_left = fred.get_series(
            series_id_left,
            observation_start=observation_start,
            observation_end=observation_end
        )
        df_right = fred.get_series(
            series_id_right,
            observation_start=observation_start,
            observation_end=observation_end
        )

        # Convertir a DataFrame
        df_left = pd.Series(df_left).dropna().reset_index()
        df_left.columns = ["date", "value_left"]
        df_left["date"] = pd.to_datetime(df_left["date"])

        df_right = pd.Series(df_right).dropna().reset_index()
        df_right.columns = ["date", "value_right"]
        df_right["date"] = pd.to_datetime(df_right["date"])

        if df_left.empty or df_right.empty:
            raise ValueError(f"No data available for one or both series")

        # Merge datos en fechas comunes
        df_merged = pd.merge(df_left, df_right, on="date", how="inner")

        if df_merged.empty:
            raise ValueError("No overlapping dates between the two series")

        # 3. Preparar directorios para guardar
        base_dir = r"C:\Users\agust\Downloads\FRED_Data"
        comparison_name = f"{series_id_left}_vs_{series_id_right}"
        comparison_dir = os.path.join(base_dir, comparison_name)
        series_subdir = os.path.join(comparison_dir, "series")
        grafico_subdir = os.path.join(comparison_dir, "grafico")
        os.makedirs(series_subdir, exist_ok=True)
        os.makedirs(grafico_subdir, exist_ok=True)

        # 3.1 Guardar datos combinados
        start_date = df_merged["date"].min().strftime("%Y-%m-%d")
        end_date = df_merged["date"].max().strftime("%Y-%m-%d")
        download_date = datetime.now().strftime("%Y%m%d")

        data_filename = f"{comparison_name}_{start_date}_to_{end_date}_downloaded_{download_date}"
        csv_path = os.path.join(series_subdir, f"{data_filename}.csv")
        xlsx_path = os.path.join(series_subdir, f"{data_filename}.xlsx")

        df_merged.to_csv(csv_path, index=False)
        df_merged.to_excel(xlsx_path, index=False)

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
        fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

        # Detectar si ambas series tienen las mismas unidades
        same_units = series_units_left.strip().lower() == series_units_right.strip().lower()

        if same_units:
            # === Graficar en el mismo eje (misma escala) ===
            ax1.plot(df_merged["date"], df_merged["value_left"],
                     linewidth=2.0, color=left_color, label=series_title_left)
            ax1.plot(df_merged["date"], df_merged["value_right"],
                     linewidth=2.0, color=right_color, label=series_title_right)
            ax1.set_xlabel('Date', fontsize=11)
            ax1.set_ylabel(f"{series_units_left}", fontsize=11)
            ax1.tick_params(axis='y', labelcolor='black')
        else:
            # === Ejes separados ===
            ax1.plot(df_merged["date"], df_merged["value_left"],
                     linewidth=2.0, color=left_color, label=series_title_left)
            ax1.set_xlabel('Date', fontsize=11)
            ax1.set_ylabel(series_title_left, fontsize=11, color=left_color)
            ax1.tick_params(axis='y', labelcolor=left_color)

            ax2 = ax1.twinx()
            ax2.plot(df_merged["date"], df_merged["value_right"],
                     linewidth=2.0, color=right_color, label=series_title_right)
            ax2.set_ylabel(series_title_right, fontsize=11, color=right_color)
            ax2.tick_params(axis='y', labelcolor=right_color)

        # 8. Configurar título
        title = f"Comparison: {series_title_left} vs {series_title_right}"
        subtitle_parts = []
        if series_units_left:
            subtitle_parts.append(f"{series_id_left} Units: {series_units_left}")
        if series_units_right and not same_units:
            subtitle_parts.append(f"{series_id_right} Units: {series_units_right}")
        subtitle = " | ".join(subtitle_parts)

        ax1.set_title(title, fontsize=12, fontweight='bold', pad=15)
        if subtitle:
            ax1.text(0.5, 1.02, subtitle, transform=ax1.transAxes,
                   fontsize=9, ha='center', style='italic')

        # 9. Formato de fechas en eje X
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')

        # 10. Grid y estilo
        ax1.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)

        # 11. Leyenda combinada
        if same_units:
            ax1.legend(loc='upper left', frameon=True, fontsize=9)
        else:
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=9)

        # 12. Nota al pie con fuente y fecha
        note = f"Source: Federal Reserve Economic Data (FRED)\nSeries: {series_id_left} vs {series_id_right} | Period: {start_date} to {end_date}"
        fig.text(0.12, -0.05, note, fontsize=9, style='italic', wrap=True)

        # 13. Ajustar layout
        plt.tight_layout()

        # 14. Guardar gráfico
        filename = f"{comparison_name}_{start_date}_to_{end_date}_plot_{download_date}.png"
        plot_path = os.path.join(grafico_subdir, filename)

        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Plot saved: {plot_path}")

        # ==================== RETURN JSON ====================
        result = {
            "tool": "plot_dual_axis",
            "series_id_left": series_id_left,
            "series_id_right": series_id_right,
            "plot_path": plot_path,
            "csv_path": csv_path,
            "excel_path": xlsx_path,  # FIX: Use xlsx_path (not excel_path)
            "start_date": start_date,
            "end_date": end_date,
            "message": f"Dual-axis plot generated for {series_id_left} vs {series_id_right}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error creating dual-axis plot for {series_id_left} vs {series_id_right}: {str(e)}")
        
        # Return error as JSON
        error_result = {
            "tool": "plot_dual_axis",
            "series_id_left": series_id_left,
            "series_id_right": series_id_right,
            "error": str(e),
            "plot_path": None,
            "csv_path": None,
            "excel_path": None
        }
        
        return json.dumps(error_result, indent=2)
