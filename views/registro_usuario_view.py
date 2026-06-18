import customtkinter as ctk
import os
from PIL import Image
from controllers.auth_controller import registrar_usuario
from utils.paths import get_resource_path


# bueno, esta es la pantalla para crear una cuenta nueva
class RegistroUsuarioView(ctk.CTkFrame):
    def __init__(self, parent, on_registro_exitoso, on_ir_login):
        super().__init__(parent, fg_color="#ffffff", corner_radius=0)
        self.on_registro_exitoso = on_registro_exitoso
        self.on_ir_login = on_ir_login
        self._build()

    def _build(self):
        # bueno, que ocupe toda la ventana
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # bueno, la tarjeta del centro
        card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=16,
            width=400,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # bueno, el logo
        logo_path = get_resource_path(os.path.join("assets", "bacilos.png"))
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, size=(100, 100))
            lbl_logo = ctk.CTkLabel(card, image=logo_ctk, text="")
            lbl_logo.image = logo_ctk
            lbl_logo.pack(pady=(20, 4))

        # bueno, título
        ctk.CTkLabel(
            card,
            text="Sistema de Análisis de Bacilos",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1e293b",
        ).pack(pady=(0, 2))

        # bueno, subtítulo
        ctk.CTkLabel(
            card,
            text="Crear cuenta",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        ).pack(pady=(0, 16))

        # bueno, campo nombre completo
        ctk.CTkLabel(
            card,
            text="Nombre completo",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=32)

        self.entry_nombre = ctk.CTkEntry(
            card,
            width=336,
            height=42,
            corner_radius=8,
            placeholder_text="Ingresa tu nombre completo",
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            text_color="#1e293b",
            font=ctk.CTkFont(size=12),
        )
        self.entry_nombre.pack(pady=(4, 8), padx=32)

        # bueno, campo usuario
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
        self.entry_usuario.pack(pady=(4, 8), padx=32)

        # bueno, campo contraseña con ojito
        ctk.CTkLabel(
            card,
            text="Contraseña",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=32)

        frame_pass = ctk.CTkFrame(card, fg_color="transparent")
        frame_pass.pack(pady=(4, 8), padx=32, fill="x")

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
        self.entry_contrasena.pack(side="left", fill="x", expand=True)

        self.btn_ojo_pass = ctk.CTkButton(
            frame_pass,
            text="👁",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#f1f5f9",
            text_color="#64748b",
            hover_color="#e2e8f0",
            font=ctk.CTkFont(size=14),
            command=lambda: self._toggle_ojo(self.entry_contrasena, self.btn_ojo_pass),
        )
        self.btn_ojo_pass.pack(side="right", padx=(6, 0))

        # bueno, campo confirmar contraseña con ojito
        ctk.CTkLabel(
            card,
            text="Confirmar contraseña",
            text_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=32)

        frame_confirm = ctk.CTkFrame(card, fg_color="transparent")
        frame_confirm.pack(pady=(4, 4), padx=32, fill="x")

        self.entry_confirmar = ctk.CTkEntry(
            frame_confirm,
            height=42,
            corner_radius=8,
            placeholder_text="Repite tu contraseña",
            show="•",
            fg_color="#ffffff",
            border_color="#cbd5e1",
            border_width=1,
            text_color="#1e293b",
            font=ctk.CTkFont(size=12),
        )
        self.entry_confirmar.pack(side="left", fill="x", expand=True)

        self.btn_ojo_conf = ctk.CTkButton(
            frame_confirm,
            text="👁",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#f1f5f9",
            text_color="#64748b",
            hover_color="#e2e8f0",
            font=ctk.CTkFont(size=14),
            command=lambda: self._toggle_ojo(self.entry_confirmar, self.btn_ojo_conf),
        )
        self.btn_ojo_conf.pack(side="right", padx=(6, 0))

        # bueno, mensaje
        self.label_mensaje = ctk.CTkLabel(
            card,
            text="",
            text_color="#ef4444",
            font=ctk.CTkFont(size=11),
        )
        self.label_mensaje.pack(pady=(0, 6))

        # bueno, botón registrarse
        ctk.CTkButton(
            card,
            text="Registrarse",
            width=336,
            height=42,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._registrar,
        ).pack(pady=(4, 10), padx=32)

        # bueno, link para volver al login
        link_frame = ctk.CTkFrame(card, fg_color="transparent")
        link_frame.pack(pady=(0, 16))

        ctk.CTkLabel(
            link_frame,
            text="¿Ya tienes cuenta? ",
            text_color="#64748b",
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

        lbl_link = ctk.CTkLabel(
            link_frame,
            text="Inicia sesión",
            text_color="#2563eb",
            font=ctk.CTkFont(size=12, weight="bold"),
            cursor="hand2",
        )
        lbl_link.pack(side="left")
        lbl_link.bind("<Button-1>", lambda e: self.on_ir_login())
        lbl_link.bind("<Enter>", lambda e: lbl_link.configure(text_color="#1d4ed8"))
        lbl_link.bind("<Leave>", lambda e: lbl_link.configure(text_color="#2563eb"))

        # bueno, atajos de teclado Enter
        self.entry_nombre.bind("<Return>", lambda e: self._registrar())
        self.entry_usuario.bind("<Return>", lambda e: self._registrar())
        self.entry_contrasena.bind("<Return>", lambda e: self._registrar())
        self.entry_confirmar.bind("<Return>", lambda e: self._registrar())

    def _toggle_ojo(self, entry, boton):
        """bueno, muestra u oculta la contraseña"""
        if entry.cget("show") == "":
            entry.configure(show="•")
            boton.configure(text="👁")
        else:
            entry.configure(show="")
            boton.configure(text="🙈")

    def _registrar(self):
        """bueno, cuando dan clic en registrarse, revisamos que todo esté bien"""
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        confirmar = self.entry_confirmar.get().strip()

        exito, mensaje = registrar_usuario(nombre, usuario, contrasena, confirmar)
        if exito:
            self.label_mensaje.configure(text=mensaje, text_color="#22c55e")
            self.after(1500, self.on_registro_exitoso)
        else:
            self.label_mensaje.configure(text=mensaje, text_color="#ef4444")
