import cv2
import os
import glob
import time
import logging
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from utils.paths import get_user_data_dir

logger = logging.getLogger(__name__)

# bueno, cuántos días guardamos las fotos viejas antes de borrarlas
_DIAS_RETENCION = 7


# bueno, esta clase maneja todo lo de la cámara del microscopio
class CamaraController:
    def __init__(self):
        self.cap = None
        self.activa = False
        self.imagenes_capturadas = []  # bueno, aquí guardamos las rutas de las fotos
        self.frame_actual = None
        self._thread = None

    @staticmethod
    def detectar_camaras(max_indices=5):
        """
        bueno, revisa qué cámaras están conectadas.
        retorna una lista de índices que respondieron.
        """
        disponibles = []
        for i in range(max_indices):
            cap = cv2.VideoCapture(i)
            # bueno, algunas cámaras USB tardan un poquito en responder
            if cap.isOpened():
                time.sleep(0.15)
                if cap.isOpened():
                    disponibles.append(i)
            cap.release()
        return disponibles

    def iniciar(self, indice=0):
        """bueno, prende la cámara con el índice que le pasemos"""
        self.cap = cv2.VideoCapture(indice)
        if self.cap.isOpened():
            # bueno, pedimos resolución 1280x720 para aprovechar mejor el microscopio
            # si la cámara no la soporta, OpenCV usará la más cercana disponible
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.activa = True
            return True
        return False

    def detener(self):
        """bueno, apaga la cámara para que no quede prendida"""
        self.activa = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def obtener_frame(self):
        """bueno, agarra la imagen que está viendo la cámara ahorita"""
        if not self.activa or not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_actual = frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        return img

    def capturar_imagen(self, carpeta=None, imagen_pil=None):
        """bueno, guarda la foto que se está viendo ahorita, opcionalmente con zoom aplicado"""
        if self.frame_actual is None and imagen_pil is None:
            return None

        carpeta = carpeta or os.path.join(get_user_data_dir(), "capturas")
        os.makedirs(carpeta, exist_ok=True)
        # bueno, le ponemos fecha y hora para que no se repitan los nombres
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nombre = f"captura_{len(self.imagenes_capturadas) + 1}_{timestamp}.png"
        ruta = os.path.join(carpeta, nombre)

        if imagen_pil is not None:
            # bueno, convertimos la imagen PIL (RGB) a BGR para OpenCV
            img_rgb = np.array(imagen_pil)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            cv2.imwrite(ruta, img_bgr)
        else:
            cv2.imwrite(ruta, self.frame_actual)
        self.imagenes_capturadas.append(ruta)
        return ruta

    def eliminar_ultima_imagen(self):
        """bueno, borra la última foto que se sacó"""
        if not self.imagenes_capturadas:
            return False

        ruta = self.imagenes_capturadas[-1]
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
            except OSError as e:
                logger.warning("No se pudo eliminar %s: %s", ruta, e)
        self.imagenes_capturadas.pop()
        return True

    def eliminar_todas(self):
        """bueno, borra todas las fotos de este análisis"""
        for ruta in self.imagenes_capturadas:
            if os.path.exists(ruta):
                try:
                    os.remove(ruta)
                except OSError as e:
                    logger.warning("No se pudo eliminar %s: %s", ruta, e)
        self.imagenes_capturadas = []

    def total_capturas(self):
        """bueno, dice cuántas fotos llevamos"""
        return len(self.imagenes_capturadas)

    def puede_capturar(self):
        """bueno, revisa si todavía podemos sacar más fotos, máximo 20"""
        return self.total_capturas() < 20

    @staticmethod
    def limpiar_archivos_antiguos(carpetas=None, dias=_DIAS_RETENCION):
        """bueno, esto borra fotos y reportes muy viejos para no llenar el disco"""
        if carpetas is None:
            base = get_user_data_dir()
            carpetas = (
                os.path.join(base, "capturas"),
                os.path.join(base, "reportes"),
            )
        limite = datetime.now() - timedelta(days=dias)
        for carpeta in carpetas:
            if not os.path.isdir(carpeta):
                continue
            for patron in ("*.png", "*.jpg", "*.jpeg", "*.pdf"):
                for ruta in glob.glob(os.path.join(carpeta, patron)):
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(ruta))
                        if mtime < limite:
                            os.remove(ruta)
                            logger.info("Archivo antiguo eliminado: %s", ruta)
                    except OSError as e:
                        logger.warning("No se pudo eliminar %s: %s", ruta, e)
