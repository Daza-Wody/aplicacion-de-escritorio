"""
Helper de rutas para funcionar tanto en desarrollo como en ejecutable PyInstaller.
"""
import sys
import os


def get_app_dir():
    """
    Retorna el directorio donde reside el ejecutable de la aplicación.
    - En desarrollo: directorio raíz del proyecto
    - En PyInstaller (frozen): directorio donde está el .exe
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """
    Retorna la ruta absoluta a un recurso de SOLO LECTURA empaquetado
    (assets, modelo, etc.). En PyInstaller onedir usa sys._MEIPASS.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = get_app_dir()
    return os.path.join(base_path, relative_path)


def get_user_data_dir():
    """
    Retorna el directorio para datos MUTABLES del usuario (BD, capturas, reportes, logs).
    En producción (frozen) usa %LOCALAPPDATA%\\BacilosApp para que los datos
    sobrevivan reinstalaciones y no dependan de permisos en Archivos de Programa.
    En desarrollo usa el directorio del proyecto.
    """
    if getattr(sys, "frozen", False):
        local_appdata = os.environ.get("LOCALAPPDATA", get_app_dir())
        data_dir = os.path.join(local_appdata, "BacilosApp")
    else:
        data_dir = get_app_dir()
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
