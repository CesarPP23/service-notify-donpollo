# db_utils.py
import pandas as pd
import pyodbc
import logging
from typing import Any, List

# Configurar logging
logger = logging.getLogger(__name__)

def get_db_connection(DB_CONFIG: dict) -> pyodbc.Connection:
    """
    Crea y retorna una conexión a SQL Server usando la configuración del archivo config.
    """
    try:
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
        )
        connection = pyodbc.connect(conn_str)
        logger.info("✅ Conexión a SQL Server establecida exitosamente")
        return connection
    except Exception as e:
        logger.error(f"❌ Error al conectar a SQL Server: {e}")
        raise

class ReporteExecutor:
    # CAMBIO 1: Se añade 'reportes_config' al constructor
    def __init__(self, db_config: dict, reportes_config: dict):
        self.db_config = db_config
        self.reportes_config = reportes_config  # Se guarda la config de reportes en la instancia

    def ejecutar_reporte(self, nombre_reporte: str, **kwargs) -> pd.DataFrame:
        """
        Ejecuta un reporte por nombre con parámetros dinámicos.
        """
        # CAMBIO 2: Se usa 'self.reportes_config' en lugar de la variable global
        if nombre_reporte not in self.reportes_config:
            raise ValueError(f"Reporte '{nombre_reporte}' no existe. Disponibles: {list(self.reportes_config.keys())}")
            
        config = self.reportes_config[nombre_reporte]
        sp_name = config['sp']
        required_params = config['params']
        
        # Validar parámetros requeridos
        missing_params = [p for p in required_params if p not in kwargs]
        if missing_params:
            raise ValueError(f"Faltan parámetros requeridos para '{nombre_reporte}': {missing_params}")
        
        # Construir SQL dinámicamente
        if required_params:
            param_placeholders = ', '.join(['?' for _ in required_params])
            sql = f"EXEC {sp_name} {param_placeholders}"
            param_values = [kwargs[p] for p in required_params]
        else:
            sql = f"EXEC {sp_name}"
            param_values = []
            
        return self._ejecutar_sp(sql, param_values, nombre_reporte)
    
    def _ejecutar_sp(self, sql: str, params: List[Any], reporte_name: str) -> pd.DataFrame:
        """Ejecuta el SP y retorna DataFrame"""
        connection = None # Se define para que exista en el bloque finally
        try:
            # CAMBIO 3: Se pasa 'self.db_config' a la función de conexión
            connection = get_db_connection(self.db_config)
            with connection.cursor() as cur:
                logger.info(f"▶ Ejecutando {reporte_name}: {sql} | Params: {params}")
                
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)

                # Buscar primer result set válido
                while True:
                    if cur.description is not None:
                        rows = cur.fetchall()
                        cols = [d[0] for d in cur.description]
                        df = pd.DataFrame.from_records(rows, columns=cols)
                        break
                    if not cur.nextset():
                        raise RuntimeError(f"El SP {reporte_name} no devolvió result sets.")

            logger.info(f"✅ {reporte_name} ejecutado: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando {reporte_name}: {e}")
            raise
        finally:
            # La lógica de cierre de conexión se mantiene intacta
            if connection:
                connection.close()
