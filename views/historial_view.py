import customtkinter as ctk
from datetime import datetime
from models.paciente import obtener_historial
from controllers.reporte_controller import generar_reporte


# bueno, esta es la pantalla donde se ven todos los análisis que se han hecho
class HistorialView(ctk.CTkFrame):
    def __init__(self, parent, on_volver):
        super().__init__(parent, fg_color="#ffffff")
        self.on_volver = on_volver
        self._build()
        self._cargar_historial()

    def _build(self):
        # bueno, que ocupe toda la ventana
        self.pack(fill="both", expand=True)

        # barra de arriba
        header = ctk.CTkFrame(self, fg_color="#2563eb", corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Historial de Analisis",
                     text_color="#ffffff",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=16)

        ctk.CTkButton(header, text="Volver", width=80, height=30,
                      corner_radius=6,
                      fg_color="#ffffff", text_color="#2563eb",
                      hover_color="#eff6ff",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self.on_volver).pack(side="right", padx=16)

        # titulo
        ctk.CTkLabel(self, text="Historial de pacientes analizados",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1e293b").pack(anchor="w", padx=20, pady=(14, 6))

        # bueno, aquí va la tabla
        scroll = ctk.CTkScrollableFrame(self, fg_color="#ffffff", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.tabla_container = scroll

        # bueno, mensaje si no hay nada
        self.label_vacio = ctk.CTkLabel(scroll, text="No hay análisis registrados aun.",
                                         text_color="#64748b",
                                         font=ctk.CTkFont(size=12))

    def _cargar_historial(self):
        """bueno, traemos todo el historial de la base de datos y lo pintamos"""
        registros = obtener_historial()

        if not registros:
            self.label_vacio.pack(pady=20)
            return

        # bueno, encabezados de la tabla
        header_frame = ctk.CTkFrame(self.tabla_container, fg_color="#f1f5f9", corner_radius=6)
        header_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(header_frame, text="Paciente", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#334155", width=200).pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(header_frame, text="Fecha de analisis", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#334155", width=150).pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(header_frame, text="Diagnostico", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#334155", width=150).pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(header_frame, text="", width=100).pack(side="left", padx=10, pady=6)

        # bueno, cada fila del historial
        for row in registros:
            nombre = f"{row['nombre']} {row['apellido_paterno']}"
            fecha = row['fecha']
            if isinstance(fecha, str):
                fecha_str = fecha
            else:
                fecha_str = str(fecha)

            fila = ctk.CTkFrame(self.tabla_container, fg_color="#ffffff", corner_radius=6)
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(fila, text=nombre, font=ctk.CTkFont(size=11),
                         text_color="#1e293b", width=200).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(fila, text=fecha_str, font=ctk.CTkFont(size=11),
                         text_color="#64748b", width=150).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(fila, text=row['diagnostico'], font=ctk.CTkFont(size=11),
                         text_color="#ef4444", width=150).pack(side="left", padx=10, pady=6)

            ctk.CTkButton(fila, text="Ver mas", width=80, height=28,
                          corner_radius=6,
                          fg_color="#2563eb", hover_color="#1d4ed8",
                          font=ctk.CTkFont(size=10, weight="bold"),
                          command=lambda r=row: self._mostrar_detalle(r)).pack(side="right", padx=10, pady=4)

    def _mostrar_detalle(self, row):
        """bueno, abre una ventanita con los detalles del analisis y un boton para hacer el pdf de nuevo"""
        popup = ctk.CTkToplevel(self)
        popup.title("Detalle del analisis")
        popup.geometry("420x420")
        popup.configure(fg_color="#ffffff")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        # datos del paciente
        nombre = f"{row['nombre']} {row['apellido_paterno']} {row['apellido_materno']}"

        ctk.CTkLabel(popup, text="Detalle del analisis",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#1e293b").pack(pady=(16, 10))

        info_frame = ctk.CTkFrame(popup, fg_color="#f8fafc", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=6)

        campos = [
            ("Paciente:", nombre),
            ("DNI:", row['dni']),
            ("Fecha:", str(row['fecha'])),
            ("Total de bacilos:", str(row['total_bacilos'])),
            ("Promedio por campo:", str(row['promedio_por_campo'])),
            ("Diagnostico:", row['diagnostico']),
        ]

        for label, valor in campos:
            fila = ctk.CTkFrame(info_frame, fg_color="transparent")
            fila.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(fila, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#334155", width=140).pack(side="left")
            ctk.CTkLabel(fila, text=valor, font=ctk.CTkFont(size=11),
                         text_color="#1e293b").pack(side="left")

        # bueno, boton para generar el pdf de nuevo
        def _generar_pdf():
            datos_paciente = {
                "nombre": row['nombre'],
                "apellido_paterno": row['apellido_paterno'],
                "apellido_materno": row['apellido_materno'],
                "dni": row['dni'],
                "edad": row['edad'],
                "sexo": row['sexo'],
                "fecha_nacimiento": row['fecha_nacimiento'],
                "domicilio": row['domicilio'],
                "medico_solicitante": row['medico_solicitante'],
                "numero_muestra": row['numero_muestra'],
                "fecha_analisis": row['fecha_analisis'],
            }
            resultado = {
                "total_bacilos": row['total_bacilos'],
                "promedio": row['promedio_por_campo'],
                "diagnostico": row['diagnostico'],
                "imagenes_procesadas": [],  # bueno, las fotos no las guardamos para regenerar
            }
            ruta = generar_reporte(row['paciente_id'], datos_paciente, resultado)
            if ruta:
                msg_label.configure(text=f"PDF guardado en:\n{ruta}", text_color="#22c55e")
            else:
                msg_label.configure(text="Error al generar PDF.", text_color="#ef4444")

        msg_label = ctk.CTkLabel(popup, text="", font=ctk.CTkFont(size=10),
                                  wraplength=360)
        msg_label.pack(pady=(10, 4))

        ctk.CTkButton(popup, text="Generar PDF de nuevo", width=200, height=36,
                      corner_radius=8,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=_generar_pdf).pack(pady=(4, 6))

        ctk.CTkButton(popup, text="Cerrar", width=120, height=34,
                      corner_radius=8,
                      fg_color="#ffffff", text_color="#334155",
                      border_width=1, border_color="#cbd5e1",
                      hover_color="#f1f5f9",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=popup.destroy).pack(pady=(0, 16))
