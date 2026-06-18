import sqlite3
import logging
from models.database import get_connection

logger = logging.getLogger(__name__)


def crear_paciente(nombre, apellido_paterno, apellido_materno, dni,
                   fecha_nacimiento, edad, sexo, celular, domicilio,
                   medico_solicitante, numero_muestra, fecha_analisis):
    """Registra un nuevo paciente. Retorna el id si fue exitoso, None si no."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pacientes (
                nombre, apellido_paterno, apellido_materno, dni,
                fecha_nacimiento, edad, sexo, celular, domicilio,
                medico_solicitante, numero_muestra, fecha_analisis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellido_paterno, apellido_materno, dni,
              fecha_nacimiento, edad, sexo, celular, domicilio,
              medico_solicitante, numero_muestra, fecha_analisis))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error("Error al crear paciente: %s", e)
        return None
    finally:
        conn.close()


def obtener_paciente_por_id(paciente_id):
    """Retorna un paciente por su id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        resultado = cursor.fetchone()
        return resultado
    except sqlite3.Error as e:
        logger.error("Error al obtener paciente %s: %s", paciente_id, e)
        return None
    finally:
        conn.close()


def dni_existe(dni):
    """Verifica si un DNI ya está registrado."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM pacientes WHERE dni = ?", (dni,))
        resultado = cursor.fetchone()
        return resultado is not None
    except sqlite3.Error as e:
        logger.error("Error al verificar DNI %s: %s", dni, e)
        return False
    finally:
        conn.close()


def guardar_resultado(paciente_id, total_bacilos, promedio_por_campo, diagnostico, usuario_id=None):
    """Guarda el resultado del análisis de un paciente."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO resultados (paciente_id, usuario_id, total_bacilos, promedio_por_campo, diagnostico)
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_id, usuario_id, total_bacilos, promedio_por_campo, diagnostico))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error("Error al guardar resultado para paciente %s: %s", paciente_id, e)
        return False
    finally:
        conn.close()


def obtener_resultado_por_paciente(paciente_id):
    """Retorna el último resultado de un paciente."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM resultados WHERE paciente_id = ?
            ORDER BY fecha DESC LIMIT 1
        """, (paciente_id,))
        resultado = cursor.fetchone()
        return resultado
    except sqlite3.Error as e:
        logger.error("Error al obtener resultado para paciente %s: %s", paciente_id, e)
        return None
    finally:
        conn.close()


def obtener_historial():
    """Retorna todo el historial de análisis con datos del paciente."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                r.id,
                r.paciente_id,
                r.total_bacilos,
                r.promedio_por_campo,
                r.diagnostico,
                r.fecha,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.dni,
                p.edad,
                p.sexo,
                p.fecha_nacimiento,
                p.domicilio,
                p.medico_solicitante,
                p.numero_muestra,
                p.fecha_analisis
            FROM resultados r
            JOIN pacientes p ON r.paciente_id = p.id
            ORDER BY r.fecha DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error("Error al obtener historial: %s", e)
        return []
    finally:
        conn.close()
