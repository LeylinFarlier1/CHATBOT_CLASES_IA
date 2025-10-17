import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import json
import glob
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_latest_dataset(base_dir: str = r"C:\Users\agust\Downloads\FRED_Data") -> dict:
    """
    Encuentra el último dataset generado por build_fred_dataset_tool.

    Args:
        base_dir: Directorio base donde se guardan los datasets

    Returns:
        dict con 'csv_path', 'xlsx_path', 'metadata_path' del último dataset
    """
    # Buscar todos los archivos CSV de datasets
    pattern = os.path.join(base_dir, "FRED_dataset_*", "*.csv")
    csv_files = glob.glob(pattern)

    if not csv_files:
        raise ValueError(f"No se encontraron datasets en {base_dir}")

    # Ordenar por fecha de modificación (más reciente primero)
    csv_files.sort(key=os.path.getmtime, reverse=True)
    latest_csv = csv_files[0]

    # Construir paths de Excel y metadata
    dataset_dir = os.path.dirname(latest_csv)
    csv_name = os.path.basename(latest_csv)

    # Buscar metadata correspondiente
    metadata_pattern = os.path.join(dataset_dir, "*_metadata_*.json")
    metadata_files = glob.glob(metadata_pattern)

    if metadata_files:
        metadata_files.sort(key=os.path.getmtime, reverse=True)
        metadata_path = metadata_files[0]
    else:
        metadata_path = None

    # Buscar Excel correspondiente
    xlsx_name = csv_name.replace('.csv', '.xlsx')
    xlsx_path = os.path.join(dataset_dir, xlsx_name)

    if not os.path.exists(xlsx_path):
        xlsx_path = None

    logger.info(f"📂 Último dataset encontrado: {latest_csv}")

    return {
        'csv_path': latest_csv,
        'xlsx_path': xlsx_path,
        'metadata_path': metadata_path,
        'dataset_dir': dataset_dir
    }


def plot_from_dataset(
    column_left: str,
    column_right: str,
    dataset_path: str = None,
    left_color: str = "#2E5090",
    right_color: str = "#C1272D"
) -> str:
    """
    Grafica dos columnas de un dataset FRED previamente construido.

    Esta herramienta cierra el ciclo ETL:
    - build_fred_dataset_tool → crea dataset con transformaciones
    - plot_from_dataset → grafica columnas del dataset sin recalcular

    Args:
        column_left: Nombre de la columna para eje izquierdo (ej: 'UNRATE')
        column_right: Nombre de la columna para eje derecho (ej: 'CPIAUCSL_YoY')
        dataset_path: Ruta al CSV del dataset. Si None, usa el último generado.
        left_color: Color para serie izquierda (default: azul)
        right_color: Color para serie derecha (default: rojo)

    Returns:
        str: Mensaje con ruta del gráfico guardado
    """

    try:
        # === 1. CARGAR DATASET ===
        if dataset_path is None:
            logger.info("📂 Buscando último dataset generado...")
            dataset_info = find_latest_dataset()
            csv_path = dataset_info['csv_path']
            metadata_path = dataset_info['metadata_path']
            dataset_dir = dataset_info['dataset_dir']
        else:
            csv_path = dataset_path
            dataset_dir = os.path.dirname(csv_path)
            # Buscar metadata en el mismo directorio
            metadata_pattern = os.path.join(dataset_dir, "*_metadata_*.json")
            metadata_files = glob.glob(metadata_pattern)
            metadata_path = metadata_files[0] if metadata_files else None

        logger.info(f"📊 Cargando dataset: {csv_path}")

        # Leer CSV
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])

        # Validar que las columnas existan
        if column_left not in df.columns:
            raise ValueError(f"Columna '{column_left}' no encontrada en el dataset. Columnas disponibles: {list(df.columns)}")
        if column_right not in df.columns:
            raise ValueError(f"Columna '{column_right}' no encontrada en el dataset. Columnas disponibles: {list(df.columns)}")

        # Eliminar filas con NaN en las columnas seleccionadas
        df_plot = df[['date', column_left, column_right]].dropna()

        if df_plot.empty:
            raise ValueError(f"No hay datos válidos para graficar {column_left} y {column_right}")

        logger.info(f"📈 Graficando {len(df_plot)} observaciones")

        # === 2. CARGAR METADATA (si existe) ===
        metadata = {}
        column_info = {}

        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if 'transformations' in metadata:
                    column_info = metadata['transformations']

        # Obtener información de las columnas
        left_info = column_info.get(column_left.split('_')[0], {})
        right_info = column_info.get(column_right.split('_')[0], {})

        left_title = left_info.get('title', column_left)
        right_title = right_info.get('title', column_right)
        left_units = left_info.get('units', '')
        right_units = right_info.get('units', '')

        # === 3. CONFIGURAR ESTILO APA ===
        plt.style.use('classic')
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'

        # === 4. CREAR FIGURA ===
        fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

        # Detectar si usar mismo eje o dual axis
        # Estrategia: si ambas columnas tienen unidades similares o están en escala comparable
        same_scale = False
        if left_units and right_units:
            same_scale = left_units.strip().lower() == right_units.strip().lower()

        if same_scale:
            # === Mismo eje ===
            ax1.plot(df_plot['date'], df_plot[column_left],
                    linewidth=2.0, color=left_color, label=left_title)
            ax1.plot(df_plot['date'], df_plot[column_right],
                    linewidth=2.0, color=right_color, label=right_title)
            ax1.set_xlabel('Date', fontsize=11)
            ax1.set_ylabel(f"{left_units}" if left_units else "Value", fontsize=11)
            ax1.tick_params(axis='y', labelcolor='black')
        else:
            # === Dual axis ===
            ax1.plot(df_plot['date'], df_plot[column_left],
                    linewidth=2.0, color=left_color, label=left_title)
            ax1.set_xlabel('Date', fontsize=11)
            ax1.set_ylabel(column_left, fontsize=11, color=left_color)
            ax1.tick_params(axis='y', labelcolor=left_color)

            ax2 = ax1.twinx()
            ax2.plot(df_plot['date'], df_plot[column_right],
                    linewidth=2.0, color=right_color, label=right_title)
            ax2.set_ylabel(column_right, fontsize=11, color=right_color)
            ax2.tick_params(axis='y', labelcolor=right_color)

        # === 5. TÍTULO Y SUBTÍTULO ===
        title = f"Comparison: {column_left} vs {column_right}"
        subtitle_parts = []
        if left_units:
            subtitle_parts.append(f"{column_left}: {left_units}")
        if right_units and not same_scale:
            subtitle_parts.append(f"{column_right}: {right_units}")
        subtitle = " | ".join(subtitle_parts)

        ax1.set_title(title, fontsize=12, fontweight='bold', pad=15)
        if subtitle:
            ax1.text(0.5, 1.02, subtitle, transform=ax1.transAxes,
                   fontsize=9, ha='center', style='italic')

        # === 6. FORMATO DE FECHAS ===
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')

        # === 7. GRID Y LEYENDA ===
        ax1.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)

        if same_scale:
            ax1.legend(loc='upper left', frameon=True, fontsize=9)
        else:
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=9)

        # === 8. NOTA AL PIE ===
        start_date = df_plot['date'].min().strftime('%Y-%m-%d')
        end_date = df_plot['date'].max().strftime('%Y-%m-%d')
        dataset_name = os.path.basename(csv_path).replace('.csv', '')

        note = f"Source: FRED Dataset - {dataset_name}\nPeriod: {start_date} to {end_date}"
        fig.text(0.12, -0.05, note, fontsize=9, style='italic', wrap=True)

        # === 9. AJUSTAR LAYOUT ===
        plt.tight_layout()

        # === 10. GUARDAR GRÁFICO ===
        download_date = datetime.now().strftime("%Y%m%d")
        filename = f"plot_{column_left}_vs_{column_right}_{download_date}.png"

        # Crear subdirectorio de gráficos si no existe
        grafico_dir = os.path.join(dataset_dir, "plots")
        os.makedirs(grafico_dir, exist_ok=True)

        plot_path = os.path.join(grafico_dir, filename)

        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"💾 Gráfico guardado: {plot_path}")

        # ==================== RETURN JSON (FIXED) ====================
        result = {
            "tool": "plot_from_dataset",
            "column_left": column_left,
            "column_right": column_right,
            "plot_path": plot_path,
            "csv_path": csv_path,  # This exists (loaded at beginning)
            "excel_path": None,     # FIX: No excel_path in this function
            "dataset_path": csv_path,  # Use csv_path as dataset_path
            "start_date": start_date,
            "end_date": end_date,
            "message": f"Plot generated from dataset: {column_left} vs {column_right}"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"❌ Error graficando desde dataset: {str(e)}")
        
        # Return error as JSON
        error_result = {
            "tool": "plot_from_dataset",
            "column_left": column_left,
            "column_right": column_right,
            "error": str(e),
            "plot_path": None,
            "csv_path": None,
            "excel_path": None
        }
        
        return json.dumps(error_result, indent=2)
