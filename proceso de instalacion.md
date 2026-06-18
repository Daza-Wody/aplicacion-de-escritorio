# Proceso de Instalación — Sistema de Análisis de Bichos

Este documento explica cómo instalar y ejecutar la aplicación en una computadora nueva, tanto en modo desarrollo como generando el ejecutable portable.

> Nota: este proyecto es parte de una tesis académica. El término "bichos" se usa de forma genérica para proteger el objeto de estudio.

---

## 1. Requisitos del sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| Sistema operativo | Windows 10/11 64 bits | Windows 11 64 bits |
| RAM | 4 GB | 8 GB |
| Espacio libre | 2 GB | 3 GB |
| Cámara | WebCam o microscopio digital USB | Microscopio digital USB 5MP+ |

---

## 2. Descargar el proyecto

Abre una terminal (PowerShell o CMD) y ejecuta:

```bash
git clone https://github.com/Daza-Wody/aplicacion-de-escritorio.git
```

Entra a la carpeta del proyecto:

```bash
cd aplicacion-de-escritorio
```

---

## 3. Instalar Python

Descarga e instala Python 3.10 o superior desde [python.org](https://www.python.org/downloads/).

Durante la instalación en Windows, marca la opción **"Add Python to PATH"**.

---

## 4. Instalar dependencias

Dentro de la carpeta del proyecto ejecuta:

```bash
pip install -r requirements.txt
```

Esto instala todas las librerías necesarias:
- CustomTkinter (interfaz gráfica)
- OpenCV (cámara)
- PyTorch + Ultralytics (modelo YOLOv11)
- ReportLab (PDF)
- entre otras.

---

## 5. Ejecutar la aplicación

```bash
python main.py
```

La app abrirá la pantalla de login. Desde ahí puedes registrar un usuario, registrar pacientes, capturar imágenes y generar reportes.

### Datos de la app

La primera vez que se ejecuta, la app crea automáticamente en `%LOCALAPPDATA%\BacilosApp\`:

```
%LOCALAPPDATA%\BacilosApp\
├── datos.db          ← Base de datos SQLite
├── capturas\         ← Imágenes capturadas/cargadas
├── reportes\         ← PDFs generados
└── bacilos_app.log   ← Logs de la aplicación
```

> Cada computadora tiene su propia base de datos. Los usuarios y pacientes registrados en una PC no aparecen automáticamente en otra.

---

## 6. Generar el ejecutable portable (.exe)

Si quieres distribuir la app como un `.exe` sin que el usuario instale Python:

### 6.1 Instalar PyInstaller

```bash
pip install pyinstaller
```

### 6.2 Ejecutar el build

```bash
python build.py
```

Esto genera la carpeta:

```
dist/BacilosApp/
├── BacilosApp.exe      ← Ejecutable principal
└── _internal/          ← Dependencias, modelo y assets
```

### 6.3 Distribuir

Comprime toda la carpeta `dist/BacilosApp/` en un `.zip`. El usuario solo descomprime y ejecuta `BacilosApp.exe`.

> **Nota:** La app no requiere el archivo `.env` para funcionar porque la consulta RENIEC está desactivada.

---

## 7. Posibles problemas

| Síntoma | Solución |
|---|---|
| "No se detectó ninguna cámara" | Verifica que el microscopio USB esté conectado. Usa el selector de cámara en la pantalla de captura. |
| La cámara se ve muy pequeña | Usa la rueda del mouse sobre la imagen para hacer zoom. |
| No aparecen usuarios registrados | Recuerda que cada PC tiene su propia `datos.db` en `%LOCALAPPDATA%\BacilosApp\`. |
| Antivirus bloquea el .exe | Añade la carpeta de la app a las exclusiones del antivirus. |

---

## 8. Soporte

Si tienes problemas:
- Revisa el log en `%LOCALAPPDATA%\BacilosApp\bacilos_app.log`
- Verifica que exista `modelo/best.pt` dentro del proyecto o del `_internal/`
