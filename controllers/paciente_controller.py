import re
from datetime import datetime
from models.paciente import crear_paciente


def registrar_paciente(nombre, apellido_paterno, apellido_materno, dni,
                       fecha_nacimiento, edad, sexo, celular, domicilio,
                       medico_solicitante, numero_muestra, fecha_analisis):
    """
    Valida y registra un nuevo paciente.
    Retorna (True, paciente_id) si fue exitoso, (False, mensaje) si no.
    """
    # Campos obligatorios
    if not nombre or not apellido_paterno or not apellido_materno:
        return False, "El nombre y apellidos son obligatorios."

    if not dni:
        return False, "El DNI es obligatorio."

    if len(dni) != 8 or not dni.isdigit():
        return False, "El DNI debe tener 8 dígitos numéricos."

    if not fecha_nacimiento:
        return False, "La fecha de nacimiento es obligatoria."

    if not re.match(r"^\d{2}/\d{2}/\d{4}$", fecha_nacimiento):
        return False, "La fecha de nacimiento debe tener formato dd/mm/aaaa."

    if not edad:
        return False, "La edad es obligatoria."

    if not edad.isdigit():
        return False, "La edad debe ser un número entero."

    edad_int = int(edad)
    if edad_int < 0 or edad_int > 150:
        return False, "La edad no es válida."

    if not sexo or sexo == "Seleccionar...":
        return False, "Seleccione el sexo del paciente."

    if not domicilio:
        return False, "El domicilio es obligatorio."

    if not medico_solicitante:
        return False, "El médico solicitante es obligatorio."

    if not numero_muestra:
        return False, "El número de muestra es obligatorio."

    if not fecha_analisis:
        return False, "La fecha del análisis es obligatoria."

    if not re.match(r"^\d{2}/\d{2}/\d{4}$", fecha_analisis):
        return False, "La fecha del análisis debe tener formato dd/mm/aaaa."

    # Celular opcional: si se ingresa, debe tener 9 dígitos
    if celular:
        if not celular.isdigit():
            return False, "El celular solo debe contener números."
        if len(celular) != 9:
            return False, "El celular debe tener 9 dígitos."

    # Validar coherencia entre fecha de nacimiento y edad
    try:
        dia, mes, anio = map(int, fecha_nacimiento.split('/'))
        fecha_nac = datetime(anio, mes, dia)
        hoy = datetime.now()
        edad_calculada = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        if abs(edad_calculada - edad_int) > 1:
            return False, f"La edad no coincide con la fecha de nacimiento. Deberia ser aproximadamente {edad_calculada} años."
    except Exception:
        return False, "Error al validar la fecha de nacimiento."

    # Guardar en base de datos
    paciente_id = crear_paciente(
        nombre, apellido_paterno, apellido_materno, dni,
        fecha_nacimiento, edad_int, sexo, celular, domicilio,
        medico_solicitante, numero_muestra, fecha_analisis
    )

    if paciente_id:
        return True, paciente_id
    return False, "Error al registrar el paciente."
