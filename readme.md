# 🔬 Sistema de Análisis

Aplicación de escritorio desarrollada en Python para el registro de pacientes y detección automática de bichos mediante una red neuronal entrenada (YOLOv11). Genera un reporte en PDF con los resultados del análisis.

---

## 🎯 Objetivo

Proveer una interfaz gráfica de escritorio donde el personal de laboratorio pueda:
1. Registrarse e iniciar sesión
2. Registrar los datos del paciente
3. Capturar 20 imágenes en tiempo real desde un telescopio conectado por USB
4. Procesar las imágenes con una red neuronal YOLOv11 para detectar y contar bichos
5. Generar un reporte PDF con los resultados del análisis

---

## 🖥️ Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.x | Lenguaje principal |
| CustomTkinter | Interfaz gráfica de escritorio (tema Light) |
| OpenCV | Captura de video desde microscopio/telescopio USB |
| PyTorch + YOLOv11 (Ultralytics) | Carga y ejecución del modelo de detección |
| ReportLab | Generación del reporte PDF |
| SQLite | Base de datos local (sin servidor) |
| Pillow (PIL) | Manipulación de imágenes |

---

## 🏗️ Arquitectura

El proyecto sigue el patrón **MVC (Model - View - Controller)**:

- **Model**: maneja la base de datos y los datos
- **View**: pantallas y componentes visuales (CustomTkinter)
- **Controller**: lógica de negocio que conecta la vista con el modelo

---

## 📁 Estructura del proyecto

```
bacilos_app/
│
├── main.py                          # Punto de entrada de la aplicación
│
├── models/
│   ├── database.py                  # Conexión SQLite, inicialización de tablas
│   ├── usuario.py                   # CRUD de usuarios (con hash SHA-256)
│   └── paciente.py                  # CRUD de pacientes y resultados
│
├── views/
│   ├── login_view.py                # Pantalla de inicio de sesión
│   ├── registro_usuario_view.py     # Pantalla de registro de nuevo usuario
│   ├── registro_paciente_view.py    # Pantalla de registro de paciente
│   ├── captura_view.py              # Pantalla de captura, eliminación y procesamiento
│   └── historial_view.py            # Pantalla de historial de análisis
│
├── controllers/
│   ├── auth_controller.py           # Lógica de login y registro de usuario
│   ├── paciente_controller.py       # Validación y registro de paciente
│   ├── camara_controller.py         # Control de cámara con OpenCV + selector de cámaras
│   ├── modelo_controller.py         # Carga y ejecución del modelo YOLOv11 .pt
│   ├── reporte_controller.py        # Generación del reporte PDF
│   └── reniec_controller.py         # Consulta de datos por DNI (requiere token)
│
├── utils/
│   ├── paths.py                     # Helper de rutas para desarrollo/PyInstaller
│   ├── config.py                    # Persistencia de configuración local
│   └── remember.py                  # Credenciales "Recordarme" ofuscadas
│
├── assets/
│   └── bacilos.png                  # Logo del sistema
│
├── modelo/
│   └── best.pt                      # Red neuronal YOLOv11 entrenada (no incluida en repo)
│
└── reportes/                        # PDFs generados se guardan aquí
```

---

## 🗄️ Base de datos (SQLite)

Archivo: `datos.db` (se crea automáticamente al iniciar la app)

### Tabla: `usuarios`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Autoincremental |
| nombre_completo | TEXT | Nombre completo del usuario |
| usuario | TEXT UNIQUE | Nombre de usuario |
| contrasena | TEXT | Contraseña hasheada con PBKDF2-HMAC-SHA256 + salt |
| fecha_creacion | TIMESTAMP | Fecha de registro |

### Tabla: `pacientes`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Autoincremental |
| nombre | TEXT | Nombre del paciente |
| apellido_paterno | TEXT | Apellido paterno |
| apellido_materno | TEXT | Apellido materno |
| dni | TEXT UNIQUE | DNI (8 dígitos) |
| fecha_nacimiento | TEXT | Formato dd/mm/aaaa |
| edad | INTEGER | Edad en años |
| sexo | TEXT | Masculino / Femenino |
| celular | TEXT | Opcional |
| domicilio | TEXT | Dirección del paciente |
| medico_solicitante | TEXT | Nombre del médico |
| numero_muestra | TEXT | Ej: MUE-001 |
| fecha_analisis | TEXT | Formato dd/mm/aaaa |
| fecha_registro | TIMESTAMP | Fecha de registro en sistema |

### Tabla: `resultados`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Autoincremental |
| paciente_id | INTEGER FK | Referencia a pacientes |
| usuario_id | INTEGER FK | Referencia al usuario que realizó el análisis |
| total_bacilos | INTEGER | Total detectado en 20 campos |
| promedio_por_campo | REAL | Promedio por campo |
| diagnostico | TEXT | Resultado según escala Ziehl-Neelsen |
| fecha | TIMESTAMP | Fecha del análisis |

---

## 🔬 Diagnóstico (Escala Ziehl-Neelsen)

| Total de bichos en los campos | Diagnóstico |
|---|---|
| 0 | Negativo (-) |
| 1 – 20 | Positivo (+) |
| 21 – 200 | Positivo (++) |
| > 200 | Positivo (+++) |

> Nota: este proyecto es parte de una tesis académica. El término "bichos" se usa aquí de forma genérica para proteger el objeto de estudio.

---

## 🖼️ Pantallas diseñadas

1. **Login** — usuario + contraseña + link a registro
2. **Registro de usuario** — nombre completo, usuario, contraseña, confirmar contraseña
3. **Registro de paciente** — todos los datos clínicos del paciente
4. **Captura** — vista en tiempo real del microscopio con selector de cámara, botones: Capturar / Cargar imágenes / Eliminar última / Procesar, miniatura de última captura, contador 0/20
5. **Reporte PDF** — datos del paciente + total bacilos + promedio + diagnóstico + imágenes procesadas en anexo
6. **Historial** — consulta de análisis anteriores con regeneración de PDF

---

## 📋 Flujo de la aplicación

```
Login
  ├── Credenciales correctas → Registro de Paciente
  └── Sin cuenta → Registro de Usuario → Login

Registro de Paciente
  └── Siguiente → Captura

Captura
  ├── Capturar imagen (hasta 20)
  ├── Eliminar última
  ├── Procesar (ejecuta YOLOv11 sobre las 20 imágenes)
  └── Ver reporte → Reporte PDF
```

---

## 📦 Dependencias

```
customtkinter
opencv-python
torch
torchvision
Pillow
reportlab
ultralytics
```

Instalar con:
```bash
pip install -r requirements.txt
```

> **Token RENIEC:** la consulta de DNI requiere un token. Configúralo mediante la variable de entorno `RENIEC_API_TOKEN` o un archivo `.env` en la carpeta del ejecutable (o `%LOCALAPPDATA%\BacilosApp\.env` en producción):
> ```
> RENIEC_API_TOKEN=tu_token_aqui
> ```

---

## ✅ Estado actual del desarrollo

| Archivo | Estado |
|---|---|
| models/database.py | ✅ Completo |
| models/usuario.py | ✅ Completo |
| models/paciente.py | ✅ Completo |
| controllers/auth_controller.py | ✅ Completo |
| controllers/paciente_controller.py | ✅ Completo |
| controllers/camara_controller.py | ✅ Completo |
| controllers/modelo_controller.py | ✅ Completo |
| controllers/reporte_controller.py | ✅ Completo |
| views/login_view.py | ✅ Completo |
| views/registro_usuario_view.py | ✅ Completo |
| views/registro_paciente_view.py | ✅ Completo |
| views/captura_view.py | ✅ Completo |
| views/historial_view.py | ✅ Completo |
| main.py | ✅ Completo |

---

## 📝 Notas importantes

- El modelo `best.pt` debe estar en la carpeta `modelo/` y fue entrenado con **YOLOv11**
- El microscopio/telescopio se conecta por **USB** y la app permite elegir entre las cámaras disponibles (no solo el índice 0)
- La app funciona **offline** para el procesamiento de imágenes
- En desarrollo la base de datos `datos.db` se crea en la raíz del proyecto; en producción se usa `%LOCALAPPDATA%\BacilosApp\`
- Las contraseñas se almacenan con **PBKDF2-HMAC-SHA256** + salt
- Las credenciales de "Recordarme" se guardan ofuscadas (XOR con clave local), no en texto plano
- Los reportes PDF se guardan en `reportes/` (desarrollo) o `%LOCALAPPDATA%\BacilosApp\reportes\` (producción)
