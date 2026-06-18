import customtkinter as ctk
from datetime import date, datetime
from controllers.paciente_controller import registrar_paciente
from controllers.reniec_controller import consultar_dni


# bueno, esta es la pantalla donde se ponen los datos del paciente antes de sacarle las fotos
class RegistroPacienteView(ctk.CTkFrame):
    def __init__(self, parent, on_siguiente, on_volver, on_historial, usuario_id=None):
        super().__init__(parent, fg_color="#ffffff", corner_radius=0)
        self.on_siguiente = on_siguiente
        self.on_volver = on_volver
        self.on_historial = on_historial
        self.usuario_id = usuario_id
        self._build()

    # bueno, esto es para que solo deje escribir números
    def _solo_numeros(self, event, max_len=None):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right",
                            "Home", "End", "Tab", "Return"):
            return
        if not event.char.isdigit():
            return "break"
        if max_len and len(event.widget.get()) >= max_len:
            return "break"

    # bueno, esto es para que solo deje escribir letras
    def _solo_letras(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right",
                            "Home", "End", "Tab", "Return", "space"):
            return
        if event.char and not event.char.isalpha() and event.char != " ":
            return "break"

    # bueno, esto pone las rayitas en la fecha automáticamente
    # tipo 13011999 se convierte en 13/01/1999
    def _formatear_fecha(self, event, entry):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right",
                            "Home", "End", "Tab"):
            return
        texto = entry.get()
        nums = ''.join(c for c in texto if c.isdigit())[:8]
        formateado = ""
        if len(nums) >= 2:
            formateado = nums[:2] + "/"
        else:
            formateado = nums
        if len(nums) >= 4:
            formateado += nums[2:4] + "/"
        elif len(nums) > 2:
            formateado += nums[2:]
        if len(nums) > 4:
            formateado += nums[4:]
        entry.delete(0, "end")
        entry.insert(0, formateado)

    # bueno, cuando escriben la fecha de nacimiento, calculamos la edad solitos
    def _calcular_edad(self, event=None):
        try:
            texto = self.entries["fecha_nacimiento"].get()
            if len(texto) == 10:
                dia, mes, anio = int(texto[:2]), int(texto[3:5]), int(texto[6:])
                fecha_nac = datetime(anio, mes, dia)
                hoy = datetime.now()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                self.entries["edad"].configure(state="normal")
                self.entries["edad"].delete(0, "end")
                self.entries["edad"].insert(0, str(edad))
                self.entries["edad"].configure(state="disabled")
        except Exception:
            pass

    def _build(self):
        # bueno, que ocupe toda la ventana
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # bueno, esto es para que se pueda hacer scroll si la pantalla es chica
        scroll = ctk.CTkScrollableFrame(self, fg_color="#ffffff", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(
            scroll,
            text="Registro de Paciente",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1e293b",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))

        # bueno, aquí van los campos que se llenan
        campos_config = [
            ("Nombre", "nombre", 1, 0, self._solo_letras),
            ("Apellido paterno", "apellido_paterno", 1, 1, self._solo_letras),
            ("Apellido materno", "apellido_materno", 1, 2, self._solo_letras),
            ("DNI (8 dígitos)", "dni", 2, 0, lambda e: self._solo_numeros(e, 8)),
            ("Fecha de nacimiento", "fecha_nacimiento", 2, 1, None),
            ("Edad", "edad", 2, 2, None),
            ("Celular (opcional)", "celular", 3, 1, lambda e: self._solo_numeros(e, 9)),
            ("Médico solicitante", "medico_solicitante", 4, 0, self._solo_letras),
            ("N° de muestra", "numero_muestra", 4, 1, None),
            ("Fecha del análisis", "fecha_analisis", 4, 2, None),
        ]

        self.entries = {}

        # bueno, creamos cada campo con su etiqueta
        for label_text, attr, fila, col, validator in campos_config:
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.grid(row=fila, column=col, padx=8, pady=8, sticky="ew")

            ctk.CTkLabel(
                frame,
                text=label_text,
                text_color="#334155",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(anchor="w")

            entry = ctk.CTkEntry(
                frame,
                width=220,
                height=40,
                corner_radius=8,
                fg_color="#ffffff",
                border_color="#cbd5e1",
                border_width=1,
                text_color="#1e293b",
                font=ctk.CTkFont(size=12),
            )
            entry.pack(fill="x")
            self.entries[attr] = entry

            if validator:
                entry.bind("<Key>", validator)

            # bueno, las fechas se formatean solitas
            if attr in ("fecha_nacimiento", "fecha_analisis"):
                entry.bind("<KeyRelease>", lambda e, ent=entry: self._formatear_fecha(e, ent))

            # bueno, cuando salen del campo de nacimiento, calculamos edad
            if attr == "fecha_nacimiento":
                entry.bind("<FocusOut>", self._calcular_edad)

            # bueno, el botón de RENIEC está oculto por ahora
            # if attr == "dni":
            #     ctk.CTkButton(
            #         frame,
            #         text="Buscar",
            #         width=80,
            #         height=32,
            #         corner_radius=8,
            #         fg_color="#2563eb",
            #         hover_color="#1d4ed8",
            #         font=ctk.CTkFont(size=11, weight="bold"),
            #         command=self._consultar_reniec,
            #     ).pack(anchor="e", pady=(6, 0))

        # bueno, texto de ejemplo en la fecha de nacimiento
        self.entries["fecha_nacimiento"].configure(placeholder_text="dd/mm/aaaa")
        # bueno, la fecha del análisis se pone solita la de hoy
        self.entries["fecha_analisis"].insert(0, date.today().strftime("%d/%m/%Y"))
        # bueno, la edad no se puede editar a mano
        if "edad" in self.entries:
            self.entries["edad"].configure(state="disabled")

        # bueno, el campo de sexo
        frame_sexo = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_sexo.grid(row=3, column=0, padx=8, pady=8, sticky="ew")
        ctk.CTkLabel(
            frame_sexo,
            text="Sexo",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.combo_sexo = ctk.CTkComboBox(
            frame_sexo,
            values=["Masculino", "Femenino"],
            width=220,
            height=40,
            corner_radius=8,
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            font=ctk.CTkFont(size=12),
        )
        self.combo_sexo.set("Seleccionar...")
        self.combo_sexo.pack(fill="x")

        # bueno, el campo de domicilio que ocupa todo el ancho
        frame_dom = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_dom.grid(row=5, column=0, columnspan=3, padx=8, pady=8, sticky="ew")
        ctk.CTkLabel(
            frame_dom,
            text="Domicilio",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.entry_domicilio = ctk.CTkEntry(
            frame_dom,
            height=40,
            corner_radius=8,
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            text_color="#1e293b",
            font=ctk.CTkFont(size=12),
        )
        self.entry_domicilio.pack(fill="x")

        # bueno, que las columnas se ajusten
        for i in range(3):
            scroll.columnconfigure(i, weight=1)

        # bueno, mensaje de error o éxito abajo
        self.label_mensaje = ctk.CTkLabel(
            scroll,
            text="",
            text_color="#ef4444",
            font=ctk.CTkFont(size=11),
        )
        self.label_mensaje.grid(row=6, column=0, columnspan=3, pady=(8, 0))

        # bueno, botones de abajo
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=3, sticky="e", pady=(20, 0))

        ctk.CTkButton(
            btn_frame,
            text="Cerrar sesion",
            width=130,
            height=40,
            corner_radius=8,
            fg_color="#ffffff",
            text_color="#ef4444",
            border_width=1,
            border_color="#ef4444",
            hover_color="#fef2f2",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_volver,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Ver historial",
            width=130,
            height=40,
            corner_radius=8,
            fg_color="#ffffff", text_color="#2563eb",
            border_width=1, border_color="#2563eb",
            hover_color="#eff6ff",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_historial,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Siguiente →",
            width=130,
            height=40,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._siguiente,
        ).pack(side="left")

    def _consultar_reniec(self):
        """bueno, cuando dan clic en buscar, vamos a internet a traer los datos del DNI"""
        dni = self.entries["dni"].get().strip()
        if len(dni) != 8 or not dni.isdigit():
            self.label_mensaje.configure(text="Ingrese un DNI valido de 8 digitos.", text_color="#ef4444")
            return

        self.label_mensaje.configure(text="Consultando RENIEC...", text_color="#2563eb")
        self.update()

        exito, datos = consultar_dni(dni)
        if exito:
            # bueno, llenamos los campos con lo que vino de RENIEC
            self.entries["nombre"].delete(0, "end")
            self.entries["nombre"].insert(0, datos.get("nombres", ""))
            self.entries["apellido_paterno"].delete(0, "end")
            self.entries["apellido_paterno"].insert(0, datos.get("apellido_paterno", ""))
            self.entries["apellido_materno"].delete(0, "end")
            self.entries["apellido_materno"].insert(0, datos.get("apellido_materno", ""))

            fecha_nac = datos.get("fecha_nacimiento", "")
            if fecha_nac:
                self.entries["fecha_nacimiento"].delete(0, "end")
                self.entries["fecha_nacimiento"].insert(0, fecha_nac)
                self._calcular_edad()

            sexo = datos.get("sexo", "")
            if sexo:
                self.combo_sexo.set(sexo)

            direccion = datos.get("direccion", "")
            if direccion:
                self.entry_domicilio.delete(0, "end")
                self.entry_domicilio.insert(0, direccion)

            self.label_mensaje.configure(text="Datos cargados desde RENIEC.", text_color="#22c55e")
        else:
            self.label_mensaje.configure(text=f"Error: {datos}", text_color="#ef4444")

    def _limpiar(self):
        """bueno, vaciamos todo para empezar de nuevo"""
        for attr, entry in self.entries.items():
            if attr == "edad":
                entry.configure(state="normal")
            entry.delete(0, "end")
            if attr == "edad":
                entry.configure(state="disabled")
        self.entries["fecha_nacimiento"].configure(placeholder_text="dd/mm/aaaa")
        self.entries["fecha_analisis"].insert(0, date.today().strftime("%d/%m/%Y"))
        self.combo_sexo.set("Seleccionar...")
        self.entry_domicilio.delete(0, "end")
        self.label_mensaje.configure(text="")

    def _siguiente(self):
        """bueno, cuando dan siguiente, revisamos y guardamos al paciente"""
        datos = {attr: entry.get().strip() for attr, entry in self.entries.items()}
        datos["sexo"] = self.combo_sexo.get()
        datos["domicilio"] = self.entry_domicilio.get().strip()

        exito, resultado = registrar_paciente(
            datos["nombre"], datos["apellido_paterno"], datos["apellido_materno"],
            datos["dni"], datos["fecha_nacimiento"], datos["edad"],
            datos["sexo"], datos["celular"], datos["domicilio"],
            datos["medico_solicitante"], datos["numero_muestra"], datos["fecha_analisis"]
        )

        if exito:
            self.label_mensaje.configure(text="")
            datos["usuario_id"] = self.usuario_id
            self.on_siguiente(resultado, datos)
        else:
            self.label_mensaje.configure(text=resultado, text_color="#ef4444")
