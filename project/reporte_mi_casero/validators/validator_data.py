import pandas as pd
from datetime import datetime, date
import logging
from typing import Optional, Set, Union

logger = logging.getLogger(__name__)

class DatosInvalidosError(Exception):
    pass

def _normalizar_fecha_obj(fecha: Union[str, datetime, date]) -> date:
    if isinstance(fecha, date) and not isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, datetime):
        return fecha.date()
    if isinstance(fecha, str):
        # Ajusta el formato si usas otro
        return datetime.strptime(fecha.strip(), "%d/%m/%Y").date()
    raise DatosInvalidosError(f"Tipo de fecha no soportado: {type(fecha)}")

def _serie_a_date(s: pd.Series) -> pd.Series:
    # Si hay números (posible serial Excel), conviértelo
    if pd.api.types.is_numeric_dtype(s):
        # Excel base 1899-12-30 (considera 1900 leap bug)
        dt = pd.to_datetime(s, origin="1899-12-30", unit="D", errors="coerce")
    else:
        dt = pd.to_datetime(s, dayfirst=True, errors="coerce", utc=True)
        # Remover tz si quedó con tz
        try:
            dt = dt.tz_convert(None)
        except Exception:
            try:
                dt = dt.tz_localize(None)
            except Exception:
                pass
    return dt.dt.date

def validar_movimientos_diarios_completos(
    df: pd.DataFrame,
    fecha: Union[str, datetime, date],
    nombre_columna_fecha: str = 'Fecha',
    columna_movimiento: str = 'Tipo de movimiento',
    movimientos_requeridos: Optional[Set[str]] = None
) -> None:
    """
    Verifica que para la 'fecha' indicada existan todos los movimientos requeridos.
    """
    logger.info("Iniciando validación de movimientos diarios completos...")

    mov_req = movimientos_requeridos or {"Stock inicial", "Ingreso", "Salida"}

    # 1) Validaciones básicas
    if df.empty:
        raise DatosInvalidosError("El DataFrame está vacío. No hay datos para validar.")
    for col in (nombre_columna_fecha, columna_movimiento):
        if col not in df.columns:
            raise DatosInvalidosError(f"Falta la columna obligatoria: '{col}'.")

    # 2) Normalizar fecha objetivo y columna de fechas
    fecha_obj = _normalizar_fecha_obj(fecha)
    fechas = _serie_a_date(df[nombre_columna_fecha])

    # 3) Filtrar por fecha
    df_dia = df.loc[fechas == fecha_obj]
    if df_dia.empty:
        # Ayuda de debug: muestra algunas fechas únicas que sí existen
        fechas_unicas = pd.Series(fechas.unique()).dropna()
        ejemplo = ", ".join(str(x) for x in fechas_unicas.sort_values().astype(str).head(5))
        raise DatosInvalidosError(
            f"No se encontró ningún registro para la fecha ({fecha_obj.strftime('%d/%m/%Y')}). "
            f"Ejemplos de fechas presentes: {ejemplo if not fechas_unicas.empty else 'ninguna'}"
        )

    # 4) Normalizar y validar movimientos
    movimientos_encontrados = set(
        df_dia[columna_movimiento]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', ' ', regex=True)
        .tolist()
    )
    mov_req_norm = {m.strip().lower().replace(r'\s+', ' ') for m in mov_req}

    faltantes = mov_req_norm - movimientos_encontrados
    if faltantes:
        faltantes_legibles = ', '.join(sorted({f.title() for f in faltantes}))
        # Ayuda de debug: muestra lo que realmente llegó ese día
        encontrados_legibles = ', '.join(sorted({m.title() for m in movimientos_encontrados}))
        raise DatosInvalidosError(
            f"Validación fallida. Faltan: {faltantes_legibles} para la fecha "
            f"({fecha_obj.strftime('%d/%m/%Y')}). Movimientos encontrados: {encontrados_legibles}"
        )

    logger.info("Validación exitosa: Todos los tipos de movimiento requeridos están presentes para la fecha indicada.")

def validar_dataframe_no_vacio(df: pd.DataFrame, nombre_df: str = "DataFrame") -> None:
    """
    Verifica si un DataFrame no está vacío.

    Args:
        df (pd.DataFrame): El DataFrame a verificar.
        nombre_df (str): Nombre descriptivo del DataFrame para mensajes de error.

    Raises:
        DatosInvalidosError: Si el DataFrame está vacío.
    """
    logger.info(f"Iniciando validación de '{nombre_df}' para verificar si está vacío.")
    
    if df.empty:
        raise DatosInvalidosError(f"El '{nombre_df}' está vacío. No hay datos para procesar.")
    
    logger.info(f"Validación exitosa: El '{nombre_df}' contiene datos.")