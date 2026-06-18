import sqlite3
import os
import logging
from utils.paths import get_user_data_dir

logger = logging.getLogger(__name__)

# Ruta de la base de datos en el directorio de datos del usuario
DB_PATH = os.path.join(get_user_data_dir(), "datos.db")


def get_connection():
    """Retorna una conexión a la base de datos SQLite con foreign keys activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _dni_tiene_unique(cursor):
    """Verifica si la columna dni de pacientes tiene un índice UNIQUE."""
    cursor.execute("PRAGMA index_list(pacientes)")
    indices = cursor.fetchall()
    for idx in indices:
        if idx["unique"]:
            # El nombre del índice proviene de metadata interna de SQLite;
            # no de input del usuario, por lo que es seguro interpolarlo aquí.
            cursor.execute(f'PRAGMA index_info("{idx["name"]}")')
            cols = cursor.fetchall()
            for col in cols:
                if col["name"] == "dni":
                    return True
    return False


def _tabla_tiene_columna(cursor, tabla, columna):
    """Verifica si una tabla tiene una columna específica."""
    cursor.execute(f'PRAGMA table_info("{tabla}")')
    columnas = [row["name"] for row in cursor.fetchall()]
    return columna in columnas


def _migrar_pacientes(cursor):
    """Quita UNIQUE de dni en pacientes si existe."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pacientes'"
    )
    if not cursor.fetchone():
        return
    if not _dni_tiene_unique(cursor):
        return

    logger.info("Migrando tabla pacientes: quitando UNIQUE de dni")
    cursor.execute("ALTER TABLE pacientes RENAME TO pacientes_old")
    cursor.execute("""
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido_paterno TEXT NOT NULL,
            apellido_materno TEXT NOT NULL,
            dni TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            edad INTEGER NOT NULL,
            sexo TEXT NOT NULL,
            celular TEXT,
            domicilio TEXT NOT NULL,
            medico_solicitante TEXT NOT NULL,
            numero_muestra TEXT NOT NULL,
            fecha_analisis TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO pacientes (
            id, nombre, apellido_paterno, apellido_materno, dni,
            fecha_nacimiento, edad, sexo, celular, domicilio,
            medico_solicitante, numero_muestra, fecha_analisis, fecha_registro
        ) SELECT id, nombre, apellido_paterno, apellido_materno, dni,
            fecha_nacimiento, edad, sexo, celular, domicilio,
            medico_solicitante, numero_muestra, fecha_analisis, fecha_registro
        FROM pacientes_old
    """)
    cursor.execute("DROP TABLE pacientes_old")
    logger.info("Migración de pacientes completada")


def _migrar_resultados(cursor):
    """Agrega usuario_id a resultados si no existe."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='resultados'"
    )
    if not cursor.fetchone():
        return
    if _tabla_tiene_columna(cursor, "resultados", "usuario_id"):
        return

    logger.info("Migrando tabla resultados: agregando usuario_id")
    cursor.execute("ALTER TABLE resultados RENAME TO resultados_old")
    cursor.execute("""
        CREATE TABLE resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            usuario_id INTEGER,
            total_bacilos INTEGER NOT NULL,
            promedio_por_campo REAL NOT NULL,
            diagnostico TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    cursor.execute("""
        INSERT INTO resultados (
            id, paciente_id, usuario_id, total_bacilos,
            promedio_por_campo, diagnostico, fecha
        ) SELECT id, paciente_id, NULL, total_bacilos,
            promedio_por_campo, diagnostico, fecha
        FROM resultados_old
    """)
    cursor.execute("DROP TABLE resultados_old")
    logger.info("Migración de resultados completada")


def initialize_db():
    """Crea las tablas si no existen y ejecuta migraciones necesarias."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migraciones
        _migrar_pacientes(cursor)
        _migrar_resultados(cursor)

        # Tabla de pacientes (para bases de datos nuevas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido_paterno TEXT NOT NULL,
                apellido_materno TEXT NOT NULL,
                dni TEXT NOT NULL,
                fecha_nacimiento TEXT NOT NULL,
                edad INTEGER NOT NULL,
                sexo TEXT NOT NULL,
                celular TEXT,
                domicilio TEXT NOT NULL,
                medico_solicitante TEXT NOT NULL,
                numero_muestra TEXT NOT NULL,
                fecha_analisis TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de resultados (para bases de datos nuevas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                usuario_id INTEGER,
                total_bacilos INTEGER NOT NULL,
                promedio_por_campo REAL NOT NULL,
                diagnostico TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        conn.commit()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error("Error inicializando base de datos: %s", e)
        conn.rollback()
        raise
    finally:
        conn.close()
