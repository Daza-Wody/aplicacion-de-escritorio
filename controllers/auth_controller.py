from models.usuario import crear_usuario, verificar_usuario, usuario_existe


def login(usuario, contrasena):
    """
    Verifica las credenciales del usuario.
    Retorna (True, datos_usuario) si es correcto, (False, mensaje) si no.
    """
    if not usuario or not contrasena:
        return False, "Por favor complete todos los campos."

    resultado = verificar_usuario(usuario, contrasena)
    if resultado:
        return True, resultado
    return False, "Usuario o contraseña incorrectos."


def registrar_usuario(nombre_completo, usuario, contrasena, confirmar_contrasena):
    """
    Registra un nuevo usuario.
    Retorna (True, mensaje) si fue exitoso, (False, mensaje) si no.
    """
    if not nombre_completo or not usuario or not contrasena or not confirmar_contrasena:
        return False, "Por favor complete todos los campos."

    if len(usuario) < 4:
        return False, "El usuario debe tener al menos 4 caracteres."

    if len(contrasena) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    if contrasena != confirmar_contrasena:
        return False, "Las contraseñas no coinciden."

    if usuario_existe(usuario):
        return False, "El nombre de usuario ya está en uso."

    exito = crear_usuario(nombre_completo, usuario, contrasena)
    if exito:
        return True, "Usuario registrado correctamente."
    return False, "Error al registrar el usuario."