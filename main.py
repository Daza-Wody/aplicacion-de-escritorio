import customtkinter as ctk
from PIL import Image
import os
import sys
import logging
import atexit
from utils.paths import get_resource_path, get_user_data_dir
from models.database import initialize_db
from views.login_view import LoginView
from views.registro_usuario_view import RegistroUsuarioView
from views.registro_paciente_view import RegistroPacienteView
from views.captura_view import CapturaView
from views.historial_view import HistorialView
from controllers.reporte_controller import generar_reporte
from controllers.camara_controller import CamaraController

# bueno, aquí preparamos para que la app guarde los mensajes en un archivo
# así si algo falla podemos ver qué pasó después
# en producción el log va en %LOCALAPPDATA%\BacilosApp, en desarrollo en la carpeta del proyecto
_log_dir = get_user_data_dir()
_log_path = os.path.join(_log_dir, "bacilos_app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(_log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


# bueno, esta es la ventana principal de toda la aplicación
# aquí es donde se muestran todas las pantallas
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Análisis de Bacilos")
        self.geometry("1200x800")
        self.minsize(1200, 800)
        self.config(bg="#ffffff")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # bueno, aquí guardamos quién inició sesión para saber quién hace los análisis
        self.usuario_actual = None
        # esto es para poder apagar la cámara cuando se cierre la ventana
        self._current_captura = None

        # bueno, ponemos el iconito arriba en la ventana
        logo_path = get_resource_path(os.path.join("assets", "bacilos.png"))
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(32, 32))
            self._logo = logo_ctk  # guardamos para que no se borre
            try:
                icon = ctk.CTkImage(light_image=logo_img, size=(64, 64))
                self.iconphoto(True, icon._light_image)
            except Exception:
                pass  # bueno, si no carga el icono no pasa nada, sigue funcionando

        # bueno, preparamos la base de datos y limpiamos archivos viejos
        initialize_db()
        CamaraController.limpiar_archivos_antiguos()

        # bueno, cuando el usuario cierra la ventana con la X, apagamos todo bien
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        atexit.register(self._liberar_recursos)

        # bueno, empezamos mostrando la pantalla de iniciar sesión
        self._mostrar_login()

    # -------------------------------------------------------
    # bueno, esto es para cambiar de pantalla
    # -------------------------------------------------------

    def _limpiar(self):
        """bueno, esto borra todo lo que hay en la ventana para poner otra pantalla"""
        for widget in self.winfo_children():
            widget.destroy()
        self.update_idletasks()

    def _mostrar_login(self):
        """bueno, muestra la pantalla donde se pone usuario y contraseña"""
        self._limpiar()
        LoginView(
            parent=self,
            on_login_exitoso=self._on_login_exitoso,
            on_ir_registro=self._mostrar_registro_usuario
        )

    def _mostrar_registro_usuario(self):
        """bueno, muestra la pantalla para crear una cuenta nueva"""
        self._limpiar()
        RegistroUsuarioView(
            parent=self,
            on_registro_exitoso=self._mostrar_login,
            on_ir_login=self._mostrar_login
        )

    def _on_login_exitoso(self, usuario):
        """bueno, cuando alguien entra bien, guardamos quién es y seguimos"""
        self.usuario_actual = usuario
        self._mostrar_registro_paciente()

    def _mostrar_registro_paciente(self):
        """bueno, muestra la pantalla para poner los datos del paciente"""
        self._limpiar()
        RegistroPacienteView(
            parent=self,
            on_siguiente=self._on_paciente_registrado,
            on_volver=self._mostrar_login,
            on_historial=self._mostrar_historial,
            usuario_id=self.usuario_actual["id"] if self.usuario_actual else None
        )

    def _on_paciente_registrado(self, paciente_id, datos_paciente):
        """bueno, cuando ya guardamos al paciente, pasamos a la cámara"""
        self._mostrar_captura(paciente_id, datos_paciente)

    def _mostrar_captura(self, paciente_id, datos_paciente):
        """bueno, esta es la pantalla más importante, donde se sacan las fotos al microscopio"""
        self._limpiar()
        self._current_captura = CapturaView(
            parent=self,
            paciente_id=paciente_id,
            datos_paciente=datos_paciente,
            usuario_id=self.usuario_actual["id"] if self.usuario_actual else None,
            on_reporte=self._on_generar_reporte,
            on_volver=self._mostrar_registro_paciente
        )

    def _on_generar_reporte(self, paciente_id, datos_paciente, resultado):
        """bueno, cuando terminamos, aquí se hace el PDF con los resultados"""
        self._last_paciente_id = paciente_id
        self._last_datos_paciente = datos_paciente
        self._last_resultado = resultado
        ruta = generar_reporte(paciente_id, datos_paciente, resultado)
        if ruta:
            self._mostrar_reporte_generado(ruta)
        else:
            self._mostrar_error_reporte()

    def _mostrar_reporte_generado(self, ruta_pdf):
        """bueno, muestra la pantalla de que todo salió bien y el PDF está listo"""
        self._limpiar()

        frame = ctk.CTkFrame(self, fg_color="#ffffff")
        frame.pack(fill="both", expand=True)

        # barra de arriba azul
        header = ctk.CTkFrame(frame, fg_color="#2563eb", corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Sistema de Análisis de Bacilos",
                     text_color="#ffffff",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(expand=True)

        # lo de en medio
        contenido = ctk.CTkFrame(frame, fg_color="transparent")
        contenido.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(contenido, text="✅",
                     font=ctk.CTkFont(size=48)).pack(pady=(0, 10))

        ctk.CTkLabel(contenido, text="Reporte generado correctamente",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1a1a2e").pack()

        ctk.CTkLabel(contenido, text=f"Guardado en: {ruta_pdf}",
                     font=ctk.CTkFont(size=11),
                     text_color="#64748b",
                     wraplength=500).pack(pady=(6, 20))

        btn_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        btn_frame.pack()

        # botón para abrir el PDF
        ctk.CTkButton(btn_frame, text="Abrir PDF", width=140, height=36,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=lambda: self._abrir_pdf(ruta_pdf)).pack(side="left",
                                                                       padx=8)

        # botón para atender a otro paciente
        ctk.CTkButton(btn_frame, text="Nuevo paciente", width=140, height=36,
                      corner_radius=8,
                      fg_color="#22c55e", hover_color="#16a34a",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._mostrar_registro_paciente).pack(side="left",
                                                                     padx=8)

        # botón para salir
        ctk.CTkButton(btn_frame, text="Cerrar sesión", width=140, height=36,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#334155",
                      border_width=1, border_color="#cbd5e1",
                      hover_color="#f1f5f9",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._mostrar_login).pack(side="left", padx=8)

    def _mostrar_error_reporte(self):
        """bueno, si el PDF no se pudo hacer, mostramos esto"""
        self._limpiar()

        frame = ctk.CTkFrame(self, fg_color="#ffffff")
        frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(frame, fg_color="#2563eb", corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Sistema de Análisis de Bacilos",
                     text_color="#ffffff",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(expand=True)

        contenido = ctk.CTkFrame(frame, fg_color="transparent")
        contenido.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(contenido, text="❌",
                     font=ctk.CTkFont(size=48)).pack(pady=(0, 10))

        ctk.CTkLabel(contenido, text="Error al generar el reporte",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1e293b").pack()

        ctk.CTkLabel(contenido,
                     text="Revisa la consola para ver el detalle del error.",
                     font=ctk.CTkFont(size=11),
                     text_color="#64748b",
                     wraplength=500).pack(pady=(6, 20))

        btn_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        btn_frame.pack()

        # bueno, botón para intentar de nuevo
        ctk.CTkButton(btn_frame, text="Reintentar", width=140, height=36,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      command=lambda: self._on_generar_reporte(
                          getattr(self, '_last_paciente_id', None),
                          getattr(self, '_last_datos_paciente', {}),
                          getattr(self, '_last_resultado', {})
                      )).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="Volver", width=140, height=36,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#334155",
                      border_width=1, border_color="#cbd5e1",
                      hover_color="#f1f5f9",
                      command=self._mostrar_registro_paciente).pack(side="left",
                                                                      padx=8)

    def _abrir_pdf(self, ruta):
        """bueno, esto abre el PDF con el programa que tenga el Windows"""
        import subprocess
        import sys
        try:
            if sys.platform == "win32":
                import os
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.call(["open", ruta])
            else:
                subprocess.call(["xdg-open", ruta])
        except Exception as e:
            logging.getLogger(__name__).error("No se pudo abrir el PDF: %s", e)

    def _liberar_recursos(self):
        """bueno, apagamos la cámara cuando se cierra todo"""
        if self._current_captura is not None:
            try:
                self._current_captura.camara.detener()
                logging.getLogger(__name__).info("Cámara liberada al cerrar")
            except Exception:
                pass
            self._current_captura = None

    def _mostrar_historial(self):
        """bueno, muestra la pantalla con todos los análisis pasados"""
        self._limpiar()
        HistorialView(
            parent=self,
            on_volver=self._mostrar_registro_paciente
        )

    def _on_cerrar(self):
        """bueno, cuando dan clic en la X de la ventana, hacemos esto"""
        self._liberar_recursos()
        self.destroy()


# bueno, aquí es donde empieza todo
if __name__ == "__main__":
    app = App()
    app.mainloop()
