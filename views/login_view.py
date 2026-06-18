import customtkinter as ctk
import os
from PIL import Image
from controllers.auth_controller import login
from utils.paths import get_resource_path
from utils.remember import guardar_credenciales, cargar_credenciales, limpiar_credenciales


# bueno, esta es la pantalla donde se pone usuario y contraseña para entrar
class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_exitoso, on_ir_registro):
        # bueno, creamos el fondo blanco que ocupa toda la ventana
        super().__init__(parent, fg_color="#ffffff", corner_radius=0)
        self.on_login_exitoso = on_login_exitoso
        self.on_ir_registro = on_ir_registro
        self._build()

    def _build(self):
        # bueno, que ocupe todo el espacio
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # bueno, la cajita blanca del medio donde van los campos
        card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=16,
            width=400,
            height=620,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)
        card.grid_propagate(False)

        # bueno, el logo de arriba
        logo_path = get_resource_path(os.path.join("assets", "bacilos.png"))
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(100, 100))
            lbl_logo = ctk.CTkLabel(card, image=logo_ctk, text="")
            lbl_logo.image = logo_ctk
            lbl_logo.pack(pady=(32, 8))

        # bueno, el título grande
        ctk.CTkLabel(
            card,
            text="Sistema de Análisis de Bacilos",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1e293b",
        ).pack(pady=(0, 2))

        # bueno, el subtítulo
        ctk.CTkLabel(
            card,
            text="Inicia sesión en tu cuenta",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        ).pack(pady=(0, 24))

        # bueno, campo de usuario
        ctk.CTkLabel(
            card,
            text="Usuario",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=32)

        self.entry_usuario = ctk.CTkEntry(
            card,
            width=336,
            height=42,
            corner_radius=8,
            placeholder_text="Ingresa tu usuario",
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            text_color="#1e293b",
            font=ctk.CTkFont(size=12),
        )
        self.entry_usuario.pack(pady=(4, 14), padx=32)

        # bueno, campo de contraseña con ojito
        ctk.CTkLabel(
            card,
            text="Contraseña",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=32)

        frame_pass = ctk.CTkFrame(card, fg_color="transparent", height=42)
        frame_pass.pack(pady=(4, 6), padx=32, fill="x")
        frame_pass.pack_propagate(False)

        self.entry_contrasena = ctk.CTkEntry(
            frame_pass,
            height=42,
            corner_radius=8,
            placeholder_text="Ingresa tu contraseña",
            show="•",
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            text_color="#1e293b",
            font=ctk.CTkFont(size=12),
        )
        self.entry_contrasena.pack(fill="both", expand=True)

        # bueno, el ojito va dentro de la caja de texto, a la derecha
        self.btn_ojo = ctk.CTkButton(
            frame_pass,
            text="👁",
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            text_color="#64748b",
            hover_color="#e2e8f0",
            font=ctk.CTkFont(size=14),
            command=self._toggle_ojo,
        )
        self.btn_ojo.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        # bueno, checkbox para recordar usuario y contraseña
        self.check_recordar = ctk.CTkCheckBox(
            card,
            text="Recordarme",
            font=ctk.CTkFont(size=11),
            text_color="#334155",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self.check_recordar.pack(anchor="w", padx=32, pady=(0, 6))

        # bueno, aquí sale el mensaje si se equivocan
        self.label_error = ctk.CTkLabel(
            card,
            text="",
            text_color="#ef4444",
            font=ctk.CTkFont(size=11),
        )
        self.label_error.pack(pady=(0, 6))

        # bueno, botón grande para entrar
        ctk.CTkButton(
            card,
            text="Ingresar",
            width=336,
            height=42,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._ingresar,
        ).pack(pady=(4, 8), padx=32)

        # bueno, link visible para ir a crear cuenta
        link_frame = ctk.CTkFrame(card, fg_color="transparent")
        link_frame.pack(pady=(8, 24))

        ctk.CTkLabel(
            link_frame,
            text="¿No tienes cuenta? ",
            text_color="#64748b",
            font=ctk.CTkFont(size=13),
        ).pack(side="left")

        lbl_link = ctk.CTkLabel(
            link_frame,
            text="Regístrate aquí",
            text_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            cursor="hand2",
        )
        lbl_link.pack(side="left")
        lbl_link.bind("<Button-1>", lambda e: self.on_ir_registro())
        lbl_link.bind("<Enter>", lambda e: lbl_link.configure(text_color="#1d4ed8"))
        lbl_link.bind("<Leave>", lambda e: lbl_link.configure(text_color="#2563eb"))

        # bueno, para que funcione dar Enter en los campos
        self.entry_usuario.bind("<Return>", lambda e: self._ingresar())
        self.entry_contrasena.bind("<Return>", lambda e: self._ingresar())

        # bueno, si hay credenciales guardadas, las ponemos solitas
        creds = cargar_credenciales()
        if creds:
            self.entry_usuario.insert(0, creds.get("usuario", ""))
            self.entry_contrasena.insert(0, creds.get("contrasena", ""))
            self.check_recordar.select()

    def _toggle_ojo(self):
        """bueno, esto muestra u oculta la contraseña cuando dan clic en el ojito"""
        if self.entry_contrasena.cget("show") == "":
            self.entry_contrasena.configure(show="•")
            self.btn_ojo.configure(text="👁")
        else:
            self.entry_contrasena.configure(show="")
            self.btn_ojo.configure(text="🙈")

    def _ingresar(self):
        """bueno, cuando dan clic en ingresar o Enter, revisamos si están bien los datos"""
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        exito, resultado = login(usuario, contrasena)
        if exito:
            self.label_error.configure(text="")
            if self.check_recordar.get():
                guardar_credenciales(usuario, contrasena)
            else:
                limpiar_credenciales()
            self.on_login_exitoso(resultado)
        else:
            self.label_error.configure(text=resultado)
