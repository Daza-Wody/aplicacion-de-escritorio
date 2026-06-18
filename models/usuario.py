import hashlib
import secrets
import sqlite3
import logging
from models.database import get_connection

logger = logging.getLogger(__name__)

"""Hash de Contraseña con libreria hashlib."""

def _hash_pbkdf2(contrasena):
    """Genera hash PBKDF2-HMAC-SHA256 con salt aleatorio."""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt.encode("ascii"),
        100_000
    )
    return f"{salt}:{pwdhash.hex()}"


def _verificar_pbkdf2(contrasena_almacenada, contrasena):
    """Verifica contraseña contra hash PBKDF2 o legacy SHA-256."""
    if ":" not in contrasena_almacenada:
        # Legacy SHA-256 (sin salt) — mantener compatibilidad transitoria
        return contrasena_almacenada == hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest()

    try:
        salt, stored_hash = contrasena_almacenada.split(":", 1)
        pwdhash = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            salt.encode("ascii"),
            100_000
        )
        return pwdhash.hex() == stored_hash
    except Exception as e:
        logger.warning("Error verificando hash de contraseña: %s", e)
        return False


def hash_contrasena(contrasena):
    """Encripta la contraseña con PBKDF2-HMAC-SHA256 + salt."""
    return _hash_pbkdf2(contrasena)


def crear_usuario(nombre_completo, usuario, contrasena):
    """Registra un nuevo usuario. Retorna True si fue exitoso."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre_completo, usuario, contrasena)
            VALUES (?, ?, ?)
        """, (nombre_completo, usuario, hash_contrasena(contrasena)))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        logger.warning("IntegrityError al crear usuario: %s", e)
        return False
    except sqlite3.Error as e:
        logger.error("Error de base de datos al crear usuario: %s", e)
        return False
    finally:
        conn.close()


def verificar_usuario(usuario, contrasena):
    """Verifica credenciales. Retorna el usuario si es correcto, None si no."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM usuarios WHERE usuario = ?
        """, (usuario,))
        resultado = cursor.fetchone()
        if resultado and _verificar_pbkdf2(resultado["contrasena"], contrasena):
            return resultado
        return None
    except sqlite3.Error as e:
        logger.error("Error de base de datos al verificar usuario: %s", e)
        return None
    finally:
        conn.close()


def usuario_existe(usuario):
    """Verifica si un nombre de usuario ya está registrado."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        return resultado is not None
    except sqlite3.Error as e:
        logger.error("Error de base de datos al verificar existencia: %s", e)
        return False
    finally:
        conn.close()
