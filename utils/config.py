"""
Bueno, aquí guardamos cositas de configuración de la app, como por ejemplo
qué cámara eligió el usuario la última vez.
"""
import json
import os
from utils.paths import get_user_data_dir

_CONFIG_FILE = os.path.join(get_user_data_dir(), "config.json")


def _leer_config():
    """bueno, trae todo el archivo de configuración o un diccionario vacío"""
    if not os.path.exists(_CONFIG_FILE):
        return {}
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _guardar_config(config):
    """bueno, guarda todo el archivo de configuración"""
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)
    except Exception:
        pass


def obtener_clave(clave, default=None):
    """bueno, trae un valor de configuración o el default si no existe"""
    config = _leer_config()
    return config.get(clave, default)


def guardar_clave(clave, valor):
    """bueno, guarda un valor de configuración"""
    config = _leer_config()
    config[clave] = valor
    _guardar_config(config)
