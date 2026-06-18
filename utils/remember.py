"""
Bueno, esto guarda el usuario y la contraseña para que no tengan que escribirlo
cada vez que abren la aplicación. Se guarda en un archivito JSON dentro de la
carpeta de datos del usuario.

IMPORTANTE: la contraseña se guarda ofuscada, NO en texto plano.
No es cifrado militar, pero evita que cualquiera que abra el archivo la lea
inmediatamente.
"""
import json
import os
import base64
import getpass
import hashlib
import platform
from utils.paths import get_user_data_dir

_REMEMBER_FILE = os.path.join(get_user_data_dir(), "remember.json")


def _obtener_clave_local():
    """
    bueno, genera una clave sencilla a partir de datos de la máquina y el usuario.
    no es perfecta, pero basta para ofuscar el archivo local.
    """
    partes = [
        getpass.getuser(),
        platform.node() or "bacilos",
        platform.system() or "windows",
        "semilla_bacilos_app_v1"
    ]
    return hashlib.sha256("|".join(partes).encode("utf-8")).digest()


def _xor_cifrar(texto):
    """cifra/descifra con XOR usando la clave local"""
    if texto is None:
        return None
    clave = _obtener_clave_local()
    datos = texto.encode("utf-8")
    cifrado = bytes(datos[i] ^ clave[i % len(clave)] for i in range(len(datos)))
    return base64.b64encode(cifrado).decode("ascii")


def _xor_descifrar(cifrado_b64):
    """descifra un texto previamente cifrado con _xor_cifrar"""
    if cifrado_b64 is None:
        return None
    clave = _obtener_clave_local()
    datos = base64.b64decode(cifrado_b64.encode("ascii"))
    descifrado = bytes(datos[i] ^ clave[i % len(clave)] for i in range(len(datos)))
    return descifrado.decode("utf-8")


def guardar_credenciales(usuario, contrasena):
    """bueno, guarda usuario y contraseña en un archivo local ofuscado"""
    try:
        with open(_REMEMBER_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "usuario": usuario,
                "contrasena": _xor_cifrar(contrasena)
            }, f)
    except Exception:
        pass


def cargar_credenciales():
    """bueno, trae el usuario y contraseña guardados, o None si no hay nada"""
    if not os.path.exists(_REMEMBER_FILE):
        return None
    try:
        with open(_REMEMBER_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
        datos["contrasena"] = _xor_descifrar(datos.get("contrasena"))
        return datos
    except Exception:
        return None


def limpiar_credenciales():
    """bueno, borra el archivo de credenciales guardadas"""
    if os.path.exists(_REMEMBER_FILE):
        try:
            os.remove(_REMEMBER_FILE)
        except Exception:
            pass
