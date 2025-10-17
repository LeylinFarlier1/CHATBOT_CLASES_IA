import os
import glob
import json
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_recent_datasets(limit: int = 5, base_dir: str = r"C:\Users\agust\Downloads\FRED_Data") -> str:
    """
    Lista los datasets más recientes creados por build_fred_dataset_tool.

    Esta herramienta resuelve el problema de contexto limitado del cliente MCP:
    - Claude puede "ver" qué datasets existen sin depender de mensajes previos
    - Permite detección automática de datasets con columnas específicas
    - Facilita reutilización sin que el usuario tenga que especificar paths

    Args:
        limit: Número máximo de datasets a listar (default: 5)
        base_dir: Directorio base donde se guardan los datasets

    Returns:
        str: Lista formateada de datasets con información clave

    Example output:
        📂 DATASETS RECIENTES (últimos 5)

        1. FRED_dataset_UNRATE_CPIAUCSL
           📅 Creado: 2025-10-11 19:30:15
           📊 Período: 1948-01-01 a 2025-08-01
           🔹 Columnas: UNRATE, CPIAUCSL_YoY
           📍 Path: C:/Users/.../dataset.csv

        2. FRED_dataset_GDP_FEDFUNDS
           📅 Creado: 2025-10-10 15:22:10
           ...
    """

    try:
        # === 1. BUSCAR TODOS LOS DATASETS ===
        pattern = os.path.join(base_dir, "FRED_dataset_*", "*.csv")
        csv_files = glob.glob(pattern)

        if not csv_files:
            return f"""📂 No se encontraron datasets en {base_dir}

💡 Para crear un dataset usa:
   build_fred_dataset_tool(series_list=['UNRATE', 'CPIAUCSL'], ...)"""

        # Ordenar por fecha de modificación (más reciente primero)
        csv_files.sort(key=os.path.getmtime, reverse=True)

        # Limitar resultados
        csv_files = csv_files[:limit]

        logger.info(f"📂 Encontrados {len(csv_files)} datasets recientes")

        # === 2. RECOLECTAR INFORMACIÓN DE CADA DATASET ===
        datasets_info = []

        for csv_path in csv_files:
            dataset_dir = os.path.dirname(csv_path)
            csv_name = os.path.basename(csv_path)

            # Nombre del dataset (sin extensión ni fechas)
            # Ejemplo: FRED_dataset_UNRATE_CPIAUCSL_GDP_2015-01-01_to_2025-08-01_built_20251011.csv
            # → FRED_dataset_UNRATE_CPIAUCSL_GDP
            dataset_name_parts = csv_name.split('_')
            if len(dataset_name_parts) >= 3:
                # Encontrar índice donde empiezan las fechas (formato YYYY-MM-DD)
                date_start_idx = None
                for i, part in enumerate(dataset_name_parts):
                    if len(part) == 4 and part.isdigit():  # Año
                        date_start_idx = i
                        break

                if date_start_idx:
                    dataset_name = '_'.join(dataset_name_parts[:date_start_idx])
                else:
                    dataset_name = csv_name.replace('.csv', '')
            else:
                dataset_name = csv_name.replace('.csv', '')

            # Fecha de creación
            creation_time = os.path.getmtime(csv_path)
            creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')

            # Leer columnas del CSV
            try:
                df = pd.read_csv(csv_path, nrows=0)  # Solo leer headers
                columns = [col for col in df.columns if col != 'date']
            except Exception as e:
                logger.warning(f"No se pudo leer {csv_name}: {e}")
                columns = []

            # Leer metadata si existe
            metadata_pattern = os.path.join(dataset_dir, "*_metadata_*.json")
            metadata_files = glob.glob(metadata_pattern)

            metadata = {}
            if metadata_files:
                try:
                    with open(metadata_files[0], 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"No se pudo leer metadata: {e}")

            # Extraer información de metadata
            date_range = metadata.get('date_range', {})
            start_date = date_range.get('start', 'N/A')
            end_date = date_range.get('end', 'N/A')
            n_observations = metadata.get('n_observations', 'N/A')
            transformations = metadata.get('transformations', {})

            # Info de transformaciones aplicadas
            transform_info = []
            for series_id, trans_data in transformations.items():
                trans_type = trans_data.get('transformation', 'none')
                if trans_type and trans_type != 'none':
                    transform_info.append(f"{series_id} → {trans_type}")

            datasets_info.append({
                'name': dataset_name,
                'creation_date': creation_date,
                'start_date': start_date,
                'end_date': end_date,
                'n_observations': n_observations,
                'columns': columns,
                'transformations': transform_info,
                'csv_path': csv_path,
                'dataset_dir': dataset_dir
            })

        # === 3. FORMATEAR SALIDA ===
        output_lines = [
            f"📂 DATASETS RECIENTES (últimos {len(datasets_info)})",
            ""
        ]

        for i, info in enumerate(datasets_info, 1):
            output_lines.append(f"{i}. {info['name']}")
            output_lines.append(f"   📅 Creado: {info['creation_date']}")

            if info['start_date'] != 'N/A' and info['end_date'] != 'N/A':
                output_lines.append(f"   📊 Período: {info['start_date']} a {info['end_date']}")

            if info['n_observations'] != 'N/A':
                output_lines.append(f"   📈 Observaciones: {info['n_observations']}")

            if info['columns']:
                columns_str = ', '.join(info['columns'])
                output_lines.append(f"   🔹 Columnas: {columns_str}")

            if info['transformations']:
                trans_str = ', '.join(info['transformations'])
                output_lines.append(f"   🔄 Transformaciones: {trans_str}")

            output_lines.append(f"   📍 Path: {info['csv_path']}")
            output_lines.append("")

        output_lines.append("💡 Para graficar columnas de un dataset usa:")
        output_lines.append("   plot_from_dataset_tool(column_left='...', column_right='...')")
        output_lines.append("   (sin especificar dataset_path usa el más reciente)")

        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"❌ Error listando datasets: {str(e)}")
        return f"""❌ Error listando datasets: {str(e)}

💡 Verifica que el directorio existe: {base_dir}"""


def find_dataset_with_columns(columns: list, base_dir: str = r"C:\Users\agust\Downloads\FRED_Data") -> dict:
    """
    Busca el dataset más reciente que contenga las columnas especificadas.

    Esta función es útil para detección automática cuando el usuario
    menciona columnas específicas sin especificar un dataset.

    Args:
        columns: Lista de nombres de columnas a buscar
        base_dir: Directorio base donde buscar

    Returns:
        dict: Info del dataset encontrado o None si no existe

    Example:
        find_dataset_with_columns(['UNRATE', 'CPIAUCSL_YoY'])
        → Returns path y info del dataset que tiene esas columnas
    """

    try:
        pattern = os.path.join(base_dir, "FRED_dataset_*", "*.csv")
        csv_files = glob.glob(pattern)

        if not csv_files:
            return None

        # Ordenar por fecha (más reciente primero)
        csv_files.sort(key=os.path.getmtime, reverse=True)

        # Buscar primer dataset que contenga todas las columnas
        for csv_path in csv_files:
            try:
                df = pd.read_csv(csv_path, nrows=0)
                dataset_columns = set(df.columns)

                # Verificar si todas las columnas requeridas están presentes
                if all(col in dataset_columns for col in columns):
                    logger.info(f"✅ Dataset encontrado con columnas {columns}: {csv_path}")
                    return {
                        'csv_path': csv_path,
                        'columns': list(dataset_columns),
                        'creation_date': datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%Y-%m-%d %H:%M:%S')
                    }
            except Exception as e:
                logger.warning(f"Error leyendo {csv_path}: {e}")
                continue

        logger.info(f"❌ No se encontró dataset con columnas {columns}")
        return None

    except Exception as e:
        logger.error(f"Error buscando dataset: {e}")
        return None
