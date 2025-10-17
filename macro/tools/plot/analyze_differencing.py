import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os
from datetime import datetime
import logging
import json  # Already imported
from statsmodels.tsa.stattools import adfuller
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_differencing(series_id: str, observation_start: str = None, observation_end: str = None) -> str:
    """
    Analiza una serie temporal calculando diferencias y test de estacionariedad.

    Calcula:
    - Serie original Xt
    - Primera diferencia: ΔXt = Xt - Xt-1
    - Segunda diferencia: Δ²Xt = Xt - 2*Xt-1 + Xt-2
    - Test de Dickey-Fuller para cada serie

    Args:
        series_id: ID de la serie de FRED (ej: 'GDP', 'CPIAUCSL', 'UNRATE')
        observation_start: Fecha de inicio (formato: 'YYYY-MM-DD'). Opcional.
        observation_end: Fecha de fin (formato: 'YYYY-MM-DD'). Opcional.

    Returns:
        str: JSON con rutas de archivos y resultados estadísticos
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

        # 3. Calcular diferencias
        df['first_diff'] = df['value'].diff()
        df['second_diff'] = df['first_diff'].diff()

        # 4. Realizar tests de Dickey-Fuller
        adf_results = {}

        # Test para serie original
        adf_original = adfuller(df['value'].dropna(), autolag='AIC')
        adf_results['original'] = {
            'ADF Statistic': adf_original[0],
            'p-value': adf_original[1],
            'Critical Value (1%)': adf_original[4]['1%'],
            'Critical Value (5%)': adf_original[4]['5%'],
            'Critical Value (10%)': adf_original[4]['10%']
        }

        # Test para primera diferencia
        adf_first = adfuller(df['first_diff'].dropna(), autolag='AIC')
        adf_results['first_diff'] = {
            'ADF Statistic': adf_first[0],
            'p-value': adf_first[1],
            'Critical Value (1%)': adf_first[4]['1%'],
            'Critical Value (5%)': adf_first[4]['5%'],
            'Critical Value (10%)': adf_first[4]['10%']
        }

        # Test para segunda diferencia
        adf_second = adfuller(df['second_diff'].dropna(), autolag='AIC')
        adf_results['second_diff'] = {
            'ADF Statistic': adf_second[0],
            'p-value': adf_second[1],
            'Critical Value (1%)': adf_second[4]['1%'],
            'Critical Value (5%)': adf_second[4]['5%'],
            'Critical Value (10%)': adf_second[4]['10%']
        }

        # 5. Preparar directorios
        base_dir = r"C:\Users\agust\Downloads\FRED_Data"
        series_dir = os.path.join(base_dir, series_id)
        series_subdir = os.path.join(series_dir, "series")
        grafico_subdir = os.path.join(series_dir, "grafico")
        os.makedirs(series_subdir, exist_ok=True)
        os.makedirs(grafico_subdir, exist_ok=True)

        # 6. Guardar datos procesados
        start_date = df["date"].min().strftime("%Y-%m-%d")
        end_date = df["date"].max().strftime("%Y-%m-%d")
        download_date = datetime.now().strftime("%Y%m%d")

        data_filename = f"{series_id}_{start_date}_to_{end_date}_differencing_{download_date}"
        csv_path = os.path.join(series_subdir, f"{data_filename}.csv")
        xlsx_path = os.path.join(series_subdir, f"{data_filename}.xlsx")

        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)

        logger.info(f"Data saved - CSV: {csv_path}")
        logger.info(f"Data saved - Excel: {xlsx_path}")

        # 7. Configurar estilo APA
        plt.style.use('classic')
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'

        # 8. Crear figura con 4 subplots (2x2)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
        fig.suptitle(f'{series_title} - Differencing Analysis', fontsize=14, fontweight='bold', y=0.995)

        # 8.1 Serie original
        ax1 = axes[0, 0]
        ax1.plot(df["date"], df["value"], linewidth=1.5, color='#2E5090')
        ax1.set_title('Original Series', fontsize=11, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=10)
        ax1.set_ylabel(f'Value ({series_units})' if series_units else 'Value', fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 8.2 Primera diferencia
        ax2 = axes[0, 1]
        ax2.plot(df["date"], df["first_diff"], linewidth=1.5, color='#D4526E')
        ax2.set_title('First Difference (ΔXt)', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=10)
        ax2.set_ylabel('ΔXt', fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 8.3 Segunda diferencia
        ax3 = axes[1, 0]
        ax3.plot(df["date"], df["second_diff"], linewidth=1.5, color='#13B5B1')
        ax3.set_title('Second Difference (Δ²Xt)', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Date', fontsize=10)
        ax3.set_ylabel('Δ²Xt', fontsize=10)
        ax3.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 8.4 Tabla con resultados ADF
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        ax4.set_title('Augmented Dickey-Fuller Test Results', fontsize=11, fontweight='bold', pad=10)

        # Crear tabla
        table_data = []
        table_data.append(['Series', 'ADF Stat', 'p-value', 'Critical 1%', 'Critical 5%', 'Stationary?'])

        for series_name, results in [('Original', adf_results['original']),
                                      ('1st Diff', adf_results['first_diff']),
                                      ('2nd Diff', adf_results['second_diff'])]:
            is_stationary = '✓' if results['p-value'] < 0.05 else '✗'
            table_data.append([
                series_name,
                f"{results['ADF Statistic']:.4f}",
                f"{results['p-value']:.4f}",
                f"{results['Critical Value (1%)']:.4f}",
                f"{results['Critical Value (5%)']:.4f}",
                is_stationary
            ])

        table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.15, 0.17, 0.15, 0.17, 0.17, 0.13])

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)

        # Estilo de tabla
        for i in range(len(table_data)):
            for j in range(len(table_data[0])):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#E8E8E8')
                    cell.set_text_props(weight='bold')
                else:
                    cell.set_facecolor('white')
                cell.set_edgecolor('black')
                cell.set_linewidth(0.5)

        # Nota al pie
        note = f"Source: Federal Reserve Economic Data (FRED) | Series: {series_id} | Period: {start_date} to {end_date}\n"
        note += "Note: Series is stationary if p-value < 0.05"
        fig.text(0.1, 0.02, note, fontsize=9, style='italic', wrap=True)

        # 9. Ajustar layout y guardar
        plt.tight_layout(rect=[0, 0.04, 1, 0.99])

        plot_filename = f"{series_id}_{start_date}_to_{end_date}_differencing_{download_date}.png"
        plot_path = os.path.join(grafico_subdir, plot_filename)

        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Plot saved: {plot_path}")

        # ==================== RETURN JSON ====================
        result = {
            "tool": "analyze_differencing",
            "series_id": series_id,
            "series_title": series_title,
            "plot_path": plot_path,
            "csv_path": csv_path,
            "excel_path": xlsx_path,  # Use xlsx_path (not excel_path)
            "start_date": start_date,
            "end_date": end_date,
            "adf_results": {
                "original": {
                    "stationary": bool(adf_results['original']['p-value'] < 0.05),
                    "p_value": float(adf_results['original']['p-value']),
                    "adf_statistic": float(adf_results['original']['ADF Statistic'])
                },
                "first_diff": {
                    "stationary": bool(adf_results['first_diff']['p-value'] < 0.05),
                    "p_value": float(adf_results['first_diff']['p-value']),
                    "adf_statistic": float(adf_results['first_diff']['ADF Statistic'])
                },
                "second_diff": {
                    "stationary": bool(adf_results['second_diff']['p-value'] < 0.05),
                    "p_value": float(adf_results['second_diff']['p-value']),
                    "adf_statistic": float(adf_results['second_diff']['ADF Statistic'])
                }
            },
            "message": f"Differencing analysis complete for {series_id}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error analyzing differencing for {series_id}: {str(e)}")
        
        # Return error as JSON
        error_result = {
            "tool": "analyze_differencing",
            "series_id": series_id,
            "error": str(e),
            "plot_path": None,
            "csv_path": None,
            "excel_path": None
        }
        
        return json.dumps(error_result, indent=2)
