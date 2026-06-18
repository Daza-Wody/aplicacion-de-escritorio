import os
import shutil
import threading
import queue
from tkinter import filedialog
from datetime import datetime
import cv2
import customtkinter as ctk
from PIL import Image
from utils.paths import get_user_data_dir
from utils.config import obtener_clave, guardar_clave
from controllers.camara_controller import CamaraController
from controllers.modelo_controller import ModeloController
from models.paciente import guardar_resultado


# bueno, esta es la pantalla más importante, donde se ven las fotos del microscopio
# y se procesan para contar los bacilos
class CapturaView(ctk.CTkFrame):
    def __init__(self, parent, paciente_id, datos_paciente, on_reporte, on_volver, usuario_id=None):
        super().__init__(parent, fg_color="#ffffff")
        self.paciente_id = paciente_id
        self.datos_paciente = datos_paciente
        self.usuario_id = usuario_id
        self.on_reporte = on_reporte
        self.on_volver = on_volver

        # bueno, preparamos la cámara y el modelo de inteligencia artificial
        self.camara = CamaraController()
        self.modelo = ModeloController()
        self.resultado = None
        self._procesando = False
        self._cola_progreso = queue.Queue()
        self._camara_img_ref = None  # bueno, esto es para que no se llene la memoria
        self._after_id = None  # bueno, para cancelar el loop de la cámara si cambian de cámara

        # bueno, esto es para el zoom con la rueda del mouse
        self.zoom_level = 1.0
        self.min_zoom = 1.0
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        self.cam_width = 960
        self.cam_height = 720

        self._build()
        self._iniciar_camara()

    def _build(self):
        # bueno, que ocupe todo
        self.pack(fill="both", expand=True)

        # bueno, barra de arriba azul con el nombre del paciente
        header = ctk.CTkFrame(self, fg_color="#2563eb", corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Sistema de Analisis de Bacilos",
                     text_color="#ffffff",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left",
                                                                     padx=16,
                                                                     expand=True)
        nombre = f"{self.datos_paciente.get('nombre', '')} {self.datos_paciente.get('apellido_paterno', '')}"
        dni = self.datos_paciente.get('dni', '')
        ctk.CTkLabel(header,
                     text=f"Paciente: {nombre}  —  DNI: {dni}",
                     text_color="#dbeafe",
                     font=ctk.CTkFont(size=11)).pack(side="right", padx=16)

        # bueno, título
        ctk.CTkLabel(self, text="Captura de imagen",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#1e293b").pack(anchor="w", padx=20, pady=(14, 6))

        # bueno, el área principal con cámara a la izquierda y botones a la derecha
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # --- lado izquierdo: la cámara en vivo ---
        lado_izq = ctk.CTkFrame(contenido, fg_color="transparent")
        lado_izq.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(lado_izq, text="Vista en tiempo real",
                     text_color="#64748b",
                     font=ctk.CTkFont(size=11)).pack(anchor="w")

        # bueno, aquí se ve la imagen del microscopio, más grande para el telescopio
        self.label_camara = ctk.CTkLabel(lado_izq, text="", fg_color="#1a1a1a",
                                          corner_radius=8, width=self.cam_width, height=self.cam_height)
        self.label_camara.pack(pady=(4, 6))
        # bueno, la rueda del mouse hace zoom
        self.label_camara.bind("<MouseWheel>", self._on_mousewheel)

        # --- lado derecho: controles y botones ---
        lado_der = ctk.CTkFrame(contenido, fg_color="transparent", width=200)
        lado_der.pack(side="right", fill="y", padx=(16, 0))
        lado_der.pack_propagate(False)

        # bueno, selector de cámara, estado y zoom arriba para que se vea en cualquier pantalla
        ctk.CTkLabel(lado_der, text="Configuracion",
                     text_color="#64748b",
                     font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0, 6))

        self.combo_camara = ctk.CTkComboBox(
            lado_der,
            values=[],
            width=180,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=10),
            dropdown_font=ctk.CTkFont(size=10),
            state="normal",
            command=self._cambiar_camara
        )
        self.combo_camara.pack(pady=(0, 6))

        estado_frame = ctk.CTkFrame(lado_der, fg_color="transparent")
        estado_frame.pack(anchor="w", pady=(0, 4))
        self.dot_estado = ctk.CTkLabel(estado_frame, text="●",
                                        text_color="#27ae60",
                                        font=ctk.CTkFont(size=12))
        self.dot_estado.pack(side="left")
        self.label_estado_texto = ctk.CTkLabel(estado_frame, text=" Camara activa",
                     text_color="#64748b",
                     font=ctk.CTkFont(size=11))
        self.label_estado_texto.pack(side="left", padx=(0, 8))

        self.label_zoom = ctk.CTkLabel(
            lado_der,
            text="Zoom: 1.0x",
            text_color="#64748b",
            font=ctk.CTkFont(size=11)
        )
        self.label_zoom.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(lado_der, text="Acciones",
                     text_color="#64748b",
                     font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0, 6))

        # bueno, contador de cuántas fotos llevamos
        self.label_contador = ctk.CTkLabel(lado_der,
                                            text="Capturas: 0 / 20",
                                            text_color="#2563eb",
                                            font=ctk.CTkFont(size=12, weight="bold"))
        self.label_contador.pack(pady=(0, 10))

        # bueno, botón para tomar foto
        ctk.CTkButton(lado_der, text="Capturar", width=180, height=40,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._capturar).pack(pady=4)

        # bueno, botón para subir fotos que ya tengan
        ctk.CTkButton(lado_der, text="Cargar imagenes", width=180, height=40,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#2563eb",
                      border_width=1, border_color="#2563eb",
                      hover_color="#eff6ff",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._cargar_imagenes).pack(pady=4)

        # bueno, botón para borrar la última foto si se equivocaron
        ctk.CTkButton(lado_der, text="Eliminar ultima", width=180, height=40,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#ef4444",
                      border_width=1, border_color="#ef4444",
                      hover_color="#fef2f2",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._eliminar).pack(pady=4)

        # bueno, botón para que la inteligencia artificial cuente los bacilos
        self.btn_procesar = ctk.CTkButton(lado_der, text="Procesar", width=180, height=40,
                      corner_radius=8,
                      fg_color="#22c55e", hover_color="#16a34a",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._procesar)
        self.btn_procesar.pack(pady=4)

        # bueno, miniatura de la última foto que se sacó
        ctk.CTkLabel(lado_der, text="Ultima captura",
                     text_color="#64748b",
                     font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(16, 4))

        self.label_miniatura = ctk.CTkLabel(lado_der, text="Sin captura",
                                             fg_color="#e2e8f0", corner_radius=6,
                                             width=180, height=130)
        self.label_miniatura.pack()

        # bueno, mensajito de abajo para decir qué está pasando
        self.label_mensaje = ctk.CTkLabel(lado_der, text="",
                                           text_color="#64748b",
                                           font=ctk.CTkFont(size=11),
                                           wraplength=180)
        self.label_mensaje.pack(pady=(10, 0))

        # bueno, botones para navegar
        nav_frame = ctk.CTkFrame(lado_der, fg_color="transparent")
        nav_frame.pack(side="bottom", pady=(10, 0))

        ctk.CTkButton(nav_frame, text="Volver", width=85, height=34,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#334155",
                      border_width=1, border_color="#cbd5e1",
                      hover_color="#f1f5f9",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._volver).pack(side="left", padx=(0, 6))

        ctk.CTkButton(nav_frame, text="Ver reporte", width=85, height=34,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._ver_reporte).pack(side="left")

    def _iniciar_camara(self):
        """bueno, detecta las cámaras y prende la que el usuario haya elegido antes"""
        camaras = self.camara.detectar_camaras(max_indices=5)
        opciones = [f"Camara {i}" for i in camaras]
        self.combo_camara.configure(values=opciones)

        if not camaras:
            self.dot_estado.configure(text_color="#ef4444")
            self.label_estado_texto.configure(text=" Camara no disponible")
            self.label_mensaje.configure(text="No se detecto ninguna camara. Use 'Cargar imagenes'.",
                                          text_color="#ef4444")
            self.combo_camara.configure(values=["Sin camaras"])
            self.combo_camara.set("Sin camaras")
            return

        ultima = obtener_clave("camara_indice", 0)
        # bueno, si la última usada ya no está, tomamos la primera disponible
        if ultima not in camaras:
            ultima = camaras[0]

        self.combo_camara.set(f"Camara {ultima}")
        exito = self.camara.iniciar(indice=ultima)
        if not exito:
            self.dot_estado.configure(text_color="#ef4444")
            self.label_estado_texto.configure(text=" Camara no disponible")
            self.label_mensaje.configure(text="No se pudo conectar la camara. Use 'Cargar imagenes'.",
                                          text_color="#ef4444")
        else:
            self._actualizar_frame()

    def _cambiar_camara(self, seleccion):
        """bueno, cuando el usuario elige otra cámara del menú, cambiamos"""
        if not seleccion.startswith("Camara "):
            return
        try:
            indice = int(seleccion.replace("Camara ", ""))
        except ValueError:
            return

        # bueno, cancelamos el loop anterior para que no haya dos corriendo a la vez
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

        self.camara.detener()
        guardar_clave("camara_indice", indice)
        exito = self.camara.iniciar(indice=indice)
        if exito:
            self.dot_estado.configure(text_color="#27ae60")
            self.label_estado_texto.configure(text=" Camara activa")
            self._actualizar_frame()
        else:
            self.dot_estado.configure(text_color="#ef4444")
            self.label_estado_texto.configure(text=" Camara no disponible")
            self.label_mensaje.configure(text=f"No se pudo conectar {seleccion}.",
                                          text_color="#ef4444")

    def _actualizar_frame(self):
        """bueno, esto actualiza la imagen de la cámara cada poquito para que se vea en vivo"""
        if self.camara.activa:
            img = self.camara.obtener_frame()
            if img:
                img_zoomed = self._aplicar_zoom(img)
                self._camara_img_ref = ctk.CTkImage(light_image=img_zoomed,
                                                    size=(self.cam_width, self.cam_height))
                self.label_camara.configure(image=self._camara_img_ref, text="")
            self._after_id = self.after(50, self._actualizar_frame)

    def _on_mousewheel(self, event):
        """bueno, la rueda del mouse acerca o aleja la imagen de la cámara"""
        # en Windows event.delta es multiplo de 120
        if event.delta > 0:
            nuevo = round(self.zoom_level + self.zoom_step, 1)
        else:
            nuevo = round(self.zoom_level - self.zoom_step, 1)
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, nuevo))
        self.label_zoom.configure(text=f"Zoom: {self.zoom_level:.1f}x")

    def _aplicar_zoom(self, img):
        """bueno, recorta el centro de la imagen según el zoom y la escala al tamaño de la cámara"""
        if self.zoom_level <= 1.0:
            return img.resize((self.cam_width, self.cam_height))

        ancho, alto = img.size
        # bueno, calculamos el trozo que vamos a mostrar según el zoom
        recorte_ancho = int(ancho / self.zoom_level)
        recorte_alto = int(alto / self.zoom_level)
        left = (ancho - recorte_ancho) // 2
        top = (alto - recorte_alto) // 2
        right = left + recorte_ancho
        bottom = top + recorte_alto
        recorte = img.crop((left, top, right, bottom))
        return recorte.resize((self.cam_width, self.cam_height))

    def _capturar(self):
        """bueno, cuando dan clic en capturar, saca la foto y la guarda"""
        if not self.camara.puede_capturar():
            self.label_mensaje.configure(text="Ya se capturaron 20 imagenes.",
                                          text_color="#ef4444")
            return

        # bueno, aplicamos el zoom a la captura para que guarde lo que se ve en pantalla
        img_para_guardar = None
        if self.camara.frame_actual is not None:
            img_rgb = cv2.cvtColor(self.camara.frame_actual, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_para_guardar = self._aplicar_zoom(img_pil)

        ruta = self.camara.capturar_imagen(imagen_pil=img_para_guardar)
        if ruta:
            self.label_contador.configure(
                text=f"Capturas: {self.camara.total_capturas()} / 20")
            self._mostrar_miniatura(ruta)
            self.label_mensaje.configure(
                text=f"Imagen {self.camara.total_capturas()} capturada.",
                text_color="#22c55e")
        else:
            self.label_mensaje.configure(text="Error al capturar imagen.",
                                          text_color="#ef4444")

    def _validar_imagen(self, ruta):
        """bueno, revisamos que el archivo sea una foto de verdad antes de copiarlo"""
        try:
            with Image.open(ruta) as img:
                img.verify()
            return True
        except Exception:
            return False

    def _cargar_imagenes(self):
        """bueno, esto abre una ventanita para elegir fotos que ya tengan guardadas"""
        if self.camara.total_capturas() >= 20:
            self.label_mensaje.configure(text="Ya se alcanzo el limite de 20 imagenes.",
                                          text_color="#ef4444")
            return

        rutas = filedialog.askopenfilenames(
            title="Seleccionar imagenes",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if not rutas:
            return

        espacio = 20 - self.camara.total_capturas()
        rutas = list(rutas)[:espacio]

        validas = []
        invalidas = 0
        capturas_dir = os.path.join(get_user_data_dir(), "capturas")
        os.makedirs(capturas_dir, exist_ok=True)
        for ruta in rutas:
            if not self._validar_imagen(ruta):
                invalidas += 1
                continue
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            nombre = f"cargada_{self.camara.total_capturas() + 1}_{timestamp}.png"
            destino = os.path.join(capturas_dir, nombre)
            shutil.copy(ruta, destino)
            self.camara.imagenes_capturadas.append(destino)
            validas.append(destino)

        msg = f"{len(validas)} imagen(es) cargada(s)."
        if invalidas:
            msg += f" ({invalidas} archivo(s) invalido(s) omitidos)"
            color = "#f59e0b"
        else:
            color = "#22c55e"

        self.label_contador.configure(
            text=f"Capturas: {self.camara.total_capturas()} / 20")
        if validas:
            self._mostrar_miniatura(validas[-1])
        self.label_mensaje.configure(text=msg, text_color=color)

    def _eliminar(self):
        """bueno, borra la última foto si se equivocaron"""
        exito = self.camara.eliminar_ultima_imagen()
        if exito:
            self.label_contador.configure(
                text=f"Capturas: {self.camara.total_capturas()} / 20")
            if self.camara.imagenes_capturadas:
                self._mostrar_miniatura(self.camara.imagenes_capturadas[-1])
            else:
                self.label_miniatura.configure(image=None, text="Sin captura")
                self.label_miniatura.image = None
            self.label_mensaje.configure(text="Ultima imagen eliminada.",
                                          text_color="#f59e0b")
        else:
            self.label_mensaje.configure(text="No hay imagenes para eliminar.",
                                          text_color="#ef4444")

    def _procesar(self):
        """bueno, aquí empieza lo bueno, la inteligencia artificial cuenta los bacilos"""
        if self.camara.total_capturas() == 0:
            self.label_mensaje.configure(text="Capture o cargue al menos una imagen.",
                                          text_color="#ef4444")
            return

        if self._procesando:
            return

        self._procesando = True
        self.btn_procesar.configure(state="disabled", text="Procesando...")
        self.label_mensaje.configure(text="Cargando modelo...", text_color="#2563eb")

        self._cola_progreso = queue.Queue()
        hilo = threading.Thread(target=self._hilo_procesar, daemon=True)
        hilo.start()
        self._chequear_progreso()

    def _hilo_procesar(self):
        """bueno, esto corre en segundo plano para que la pantalla no se congele"""
        exito, msg = self.modelo.cargar_modelo()
        if not exito:
            self._cola_progreso.put(("error", msg))
            return

        total = 0
        rutas_procesadas = []
        total_imagenes = len(self.camara.imagenes_capturadas)

        # bueno, vamos foto por foto contando bacilos
        for i, ruta in enumerate(self.camara.imagenes_capturadas):
            self._cola_progreso.put(("progreso", i + 1, total_imagenes))
            cantidad, ruta_proc, _ = self.modelo.procesar_imagen(ruta)
            total += cantidad
            if ruta_proc:
                rutas_procesadas.append(ruta_proc)
            else:
                rutas_procesadas.append(ruta)

        self._cola_progreso.put(("completado", total, rutas_procesadas))

    def _chequear_progreso(self):
        """bueno, esto revisa cómo va el procesamiento y actualiza la pantalla"""
        try:
            while True:
                msg = self._cola_progreso.get_nowait()
                tipo = msg[0]

                if tipo == "error":
                    self.label_mensaje.configure(text=msg[1], text_color="#ef4444")
                    self._finalizar_proceso()
                    return

                elif tipo == "progreso":
                    actual, total_img = msg[1], msg[2]
                    self.label_mensaje.configure(
                        text=f"Procesando {actual}/{total_img}...",
                        text_color="#2563eb")

                elif tipo == "completado":
                    total, rutas_procesadas = msg[1], msg[2]
                    total_img = len(self.camara.imagenes_capturadas)
                    promedio = round(total / total_img, 2) if total_img > 0 else 0
                    diagnostico = self.modelo._calcular_diagnostico(total)

                    # bueno, guardamos los resultados en la base de datos
                    guardar_resultado(self.paciente_id, total, promedio, diagnostico, self.usuario_id)

                    self.resultado = {
                        "total_bacilos": total,
                        "promedio": promedio,
                        "diagnostico": diagnostico,
                        "imagenes_procesadas": rutas_procesadas
                    }

                    self.label_mensaje.configure(
                        text=f"Procesado. Total: {total} bacilos.",
                        text_color="#22c55e")

                    self._mostrar_popup_exito(total, promedio, diagnostico)
                    self._finalizar_proceso()
                    return
        except queue.Empty:
            pass

        self.after(100, self._chequear_progreso)

    def _finalizar_proceso(self):
        """bueno, esto devuelve el botón a la normalidad"""
        self._procesando = False
        self.btn_procesar.configure(state="normal", text="Procesar")

    def _mostrar_popup_exito(self, total, promedio, diagnostico):
        """bueno, muestra una ventanita felicitando que terminó"""
        popup = ctk.CTkToplevel(self)
        popup.title("Procesamiento completado")
        popup.geometry("360x220")
        popup.configure(fg_color="#ffffff")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="OK",
                     font=ctk.CTkFont(size=48)).pack(pady=(16, 6))
        ctk.CTkLabel(popup, text="Analisis completado",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1e293b").pack()
        ctk.CTkLabel(popup,
                     text=f"Total: {total} bacilos | Promedio: {promedio}\nDiagnostico: {diagnostico}",
                     font=ctk.CTkFont(size=12),
                     text_color="#64748b").pack(pady=(6, 14))

        ctk.CTkButton(popup, text="Aceptar", width=120, height=36,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=popup.destroy).pack(pady=(0, 16))

    def _mostrar_miniatura(self, ruta):
        """bueno, muestra la última foto chiquita al lado de los botones"""
        try:
            img = Image.open(ruta).resize((180, 130))
            ctk_img = ctk.CTkImage(light_image=img, size=(180, 130))
            self.label_miniatura.configure(image=ctk_img, text="")
            self.label_miniatura.image = ctk_img
        except Exception:
            pass

    def _ver_reporte(self):
        """bueno, cuando dan ver reporte, vamos a la pantalla del PDF"""
        if not self.resultado:
            self.label_mensaje.configure(text="Primero procese las imagenes.",
                                          text_color="#ef4444")
            return
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.camara.detener()
        self.on_reporte(self.paciente_id, self.datos_paciente, self.resultado)

    def _volver(self):
        """bueno, para regresar a la pantalla anterior"""
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.camara.detener()
        self.on_volver()
