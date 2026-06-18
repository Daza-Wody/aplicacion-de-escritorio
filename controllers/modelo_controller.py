import os
import logging
import cv2
import numpy as np
from PIL import Image
from utils.paths import get_resource_path


# bueno, esta clase carga la red neuronal y cuenta los bacilos en las fotos
class ModeloController:
    def __init__(self, ruta_modelo=None):
        # bueno, si no nos dicen dónde está el modelo, usamos el de por defecto
        self.ruta_modelo = ruta_modelo or get_resource_path("modelo/best.pt")
        self.modelo = None

    def cargar_modelo(self):
        """bueno, aquí cargamos el cerebro de la red neuronal, o sea el modelo de segmentación entrenado"""
        if not os.path.exists(self.ruta_modelo):
            return False, f"No se encontró el modelo en: {self.ruta_modelo}"

        try:
            from ultralytics import YOLO
            self.modelo = YOLO(self.ruta_modelo)
            return True, "Modelo de segmentación cargado correctamente."
        except Exception as e:
            return False, f"Error al cargar el modelo: {str(e)}"

    def procesar_imagen(self, ruta_imagen):
        """bueno, esta es la parte donde la red neuronal mira la foto y dice cuántos bacilos hay"""
        if self.modelo is None:
            return 0, None, 0

        if not os.path.exists(ruta_imagen):
            return 0, None, 0

        try:
            results = self.modelo(ruta_imagen, verbose=False)
            result = results[0]

            cantidad = 0
            total_pixeles = 0

            # bueno, filtros para descartar detecciones que no sean bacilos
            # MIN_AREA: area minima en pixeles que debe tener una mascara para ser contada
            #            esto elimina manchitas pequenas de ruido
            # MIN_ASPECT_RATIO: relacion largo/ancho minima. Los bacilos son alargados,
            #                   asi que descartamos particulas redondas
            MIN_AREA = 20
            MIN_ASPECT_RATIO = 2.0

            # bueno, el modelo hace segmentación, o sea pinta píxel por píxil donde están los bacilos
            if result.masks is not None:
                masks = result.masks.data.cpu().numpy()

                for mask in masks:
                    # bueno, el area es la cantidad de pixeles blancos de la mascara
                    area = int(np.sum(mask))
                    if area < MIN_AREA:
                        continue  # muy chiquito, lo ignoramos

                    # bueno, calculamos la caja que rodea la mascara para saber su forma
                    filas, columnas = np.where(mask > 0)
                    if len(filas) == 0 or len(columnas) == 0:
                        continue

                    alto = filas.max() - filas.min() + 1
                    ancho = columnas.max() - columnas.min() + 1
                    if ancho == 0:
                        continue

                    relacion = max(alto, ancho) / min(alto, ancho)
                    if relacion < MIN_ASPECT_RATIO:
                        continue  # muy redondo, no es bacilo

                    # bueno, si paso los filtros, lo contamos
                    cantidad += 1
                    total_pixeles += area

            # bueno, por si acaso no hay máscaras, contamos cajitas
            elif result.boxes is not None:
                # bueno, aqui podriamos aplicar filtros similares con las cajas
                cantidad = len(result.boxes)

            # bueno, dibujamos las máscaras/recuadros encima de la foto para que el doctor vea
            try:
                # labels=False y conf=False para que solo se vean los recuadros, sin texto de confianza
                img_bgr = result.plot(labels=False, conf=False)
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
            except Exception as plot_err:
                logging.getLogger(__name__).warning("No se pudo pintar las máscaras, usamos la original: %s", plot_err)
                img_pil = Image.open(ruta_imagen).convert("RGB")

            # bueno, guardamos la foto con los bacilos pintados
            ruta_procesada = ruta_imagen.replace(".png", "_procesada.png")
            img_pil.save(ruta_procesada)

            return cantidad, ruta_procesada, total_pixeles

        except Exception as e:
            logging.getLogger(__name__).exception("Error al procesar la foto %s", ruta_imagen)
            return 0, None, 0

    def procesar_todas(self, rutas_imagenes):
        """bueno, procesa todas las fotos y saca el promedio para el diagnóstico"""
        total_bacilos = 0
        total_pixeles = 0
        rutas_procesadas = []

        for ruta in rutas_imagenes:
            cantidad, ruta_proc, pixeles = self.procesar_imagen(ruta)
            total_bacilos += cantidad
            total_pixeles += pixeles
            if ruta_proc:
                rutas_procesadas.append(ruta_proc)
            else:
                rutas_procesadas.append(ruta)

        campos = len(rutas_imagenes) if rutas_imagenes else 1
        promedio = round(total_bacilos / campos, 2)
        diagnostico = self._calcular_diagnostico(promedio)

        logging.getLogger(__name__).info(
            "Total bacilos: %s | Promedio: %s | Diagnóstico: %s",
            total_bacilos, promedio, diagnostico
        )

        return total_bacilos, promedio, diagnostico, rutas_procesadas

    def _calcular_diagnostico(self, promedio):
        """bueno, según cuántos bacilos salen, damos el resultado de la prueba"""
        if promedio == 0:
            return "Negativo (-)"
        elif promedio < 1:
            return "Dudoso (±)"
        elif 1 <= promedio <= 9:
            return "Positivo (+)"
        elif 10 <= promedio <= 99:
            return "Positivo (++)"
        else:
            return "Positivo (+++)"
