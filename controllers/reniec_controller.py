import os
import time
import logging
import requests
from utils.paths import get_app_dir, get_user_data_dir

logger = logging.getLogger(__name__)

# bueno, aquí va el token para consultar los datos del DNI.
# NUNCA se guarda en el código; se obtiene de una variable de entorno o un archivo .env
# junto al ejecutable o en la carpeta de datos del usuario.

def _leer_token_env(env_path):
    """lee el token de un archivo .env si existe"""
    if not os.path.exists(env_path):
        return None
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea.startswith("RENIEC_API_TOKEN="):
                    token = linea.split("=", 1)[1].strip().strip('"').strip("'")
                    if token:
                        return token
    except Exception:
        pass
    return None


def _cargar_token():
    """
    bueno, busca el token en este orden:
    1. Variable de entorno RENIEC_API_TOKEN
    2. Archivo .env en la carpeta de datos del usuario
    3. Archivo .env junto al ejecutable/app
    """
    token = os.getenv("RENIEC_API_TOKEN")
    if token:
        return token.strip()

    token = _leer_token_env(os.path.join(get_user_data_dir(), ".env"))
    if token:
        return token

    token = _leer_token_env(os.path.join(get_app_dir(), ".env"))
    if token:
        return token
    return None


API_TOKEN = _cargar_token()

# bueno, para no saturar la página de RENIEC, esperamos entre consultas
_ULTIMA_CONSULTA = 0.0
_MIN_INTERVALO = 1.5


# bueno, esta función va a internet y trae los datos de la persona por su DNI
def consultar_dni(dni, token=None):
    global _ULTIMA_CONSULTA

    token = token or API_TOKEN
    if not token:
        logger.error("No hay token de API RENIEC configurado")
        return False, (
            "Token de API RENIEC no configurado. "
            "Configure la variable de entorno RENIEC_API_TOKEN o un archivo .env junto al ejecutable."
        )

    # bueno, revisamos que no estén consultando muy rápido
    ahora = time.time()
    tiempo_restante = _MIN_INTERVALO - (ahora - _ULTIMA_CONSULTA)
    if tiempo_restante > 0:
        return False, f"Espere {tiempo_restante:.1f} segundos entre consultas."
    _ULTIMA_CONSULTA = ahora

    try:
        url = "https://kmente.com/api/v1/reniec"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        data = {"dni": dni}

        response = requests.get(url, headers=headers, params=data, timeout=15)

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp.get("ok"):
                raw = json_resp.get("data", {})
                return True, _normalizar_respuesta(raw)
            else:
                msg = json_resp.get("message", "Respuesta no exitosa de la API.")
                logger.warning("API RENIEC respuesta no exitosa: %s", msg)
                return False, msg
        else:
            logger.warning("API RENIEC HTTP %s: %s", response.status_code, response.text)
            return False, f"Error HTTP {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        logger.warning("Timeout en consulta RENIEC")
        return False, "Tiempo de espera agotado. Verifica tu conexion a internet."
    except requests.exceptions.ConnectionError:
        logger.warning("Error de conexion en consulta RENIEC")
        return False, "No se pudo conectar con el servidor de RENIEC."
    except Exception as e:
        logger.exception("Error inesperado en consulta RENIEC")
        return False, f"Error inesperado: {str(e)}"


# bueno, esto ordena los datos que vienen de RENIEC para que se vean bonitos
def _normalizar_respuesta(raw):
    sexo_raw = raw.get("sexo", "")
    sexo = ""
    if sexo_raw:
        sexo_lower = sexo_raw.lower()
        if sexo_lower == "masculino":
            sexo = "Masculino"
        elif sexo_lower == "femenino":
            sexo = "Femenino"

    data = {
        "nombres": raw.get("preNombres", ""),
        "apellido_paterno": raw.get("apePaterno", ""),
        "apellido_materno": raw.get("apeMaterno", ""),
        "fecha_nacimiento": raw.get("feNacimiento", ""),
        "sexo": sexo,
        "direccion": raw.get("Direccion", raw.get("desDireccion", "")),
    }
    return data
