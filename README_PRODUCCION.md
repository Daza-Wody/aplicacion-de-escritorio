# Guía de Producción — Sistema de Análisis de Bacilos

Este documento explica cómo empaquetar la aplicación para distribución en clínicas/laboratorios.

---

## 1. Requisitos del sistema (máquina de destino)

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| Sistema operativo | Windows 10/11 64 bits | Windows 11 64 bits |
| RAM | 4 GB | 8 GB |
| Espacio libre | 2 GB | 3 GB |
| Cámara | WebCam/USB microscope (índice 0) | Microscopio digital USB 5MP+ |
| Internet | Solo para consulta RENIEC | Conexión estable |

---

## 2. Preparar entorno de build (máquina de desarrollo)

### 2.1 Instalar dependencias de build

```bash
# En la carpeta del proyecto
pip install pyinstaller
```

> **Nota:** No es obligatorio usar `virtualenv`, pero sí recomendado para evitar incluir paquetes no deseados en el ejecutable.

### 2.2 Configurar token de RENIEC (obligatorio)

El token de la API RENIEC **no está incluido en el código** por seguridad. Configúralo de una de estas formas:

1. **Variable de entorno** (recomendado para desarrollo):

   ```powershell
   # Windows PowerShell
   $env:RENIEC_API_TOKEN = "tu_token_aqui"
   ```

2. **Archivo `.env`** junto al ejecutable en producción:

   ```
   RENIEC_API_TOKEN=tu_token_aqui
   ```

   > Ver sección 5 para saber dónde colocar el archivo `.env` según el método de distribución.

---

## 3. Generar el ejecutable

```bash
python build.py
```

Esto crea la carpeta:

```
dist/BacilosApp/
├── BacilosApp.exe          ← Ejecutable principal
├── _internal/              ← Dependencias, Python, assets, modelo
│   ├── assets/
│   ├── modelo/best.pt
│   └── ... (librerías)
```

**Tamaño estimado:** ~900 MB (PyTorch + OpenCV + Ultralytics ocupan la mayor parte).

### Opciones de build

Edita `build.py` si necesitas ajustar:

- **`--windowed`** → Sin ventana de consola (modo GUI).
- **`--onedir`** → Carpeta con `.exe` + dependencias. Recomendado sobre `--onefile` porque:
  - El modelo ML no se extrae a `%TEMP%` en cada arranque (más rápido).
  - La base de datos y archivos generados no compiten con el archivo único.
  - Menor consumo de RAM en arranque.

---

## 4. Verificar el build

1. Ve a `dist/BacilosApp/`.
2. Haz doble clic en `BacilosApp.exe`.
3. La app debería abrirse y mostrar la pantalla de login.
4. Revisa que no haya errores en el archivo de log:
   ```
   %LOCALAPPDATA%\BacilosApp\bacilos_app.log
   ```

### Posibles problemas

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| "BacilosApp.exe dejó de funcionar" al inicio | Antivirus bloquea el bootloader de PyInstaller | Ejecuta `build.py` con `--noupx` o añade excepción en el antivirus |
| No carga el modelo | `best.pt` no encontrado | Verifica que exista `dist/BacilosApp/_internal/modelo/best.pt` |
| No aparece el logo | Assets no empaquetados | Verifica `dist/BacilosApp/_internal/assets/` |
| Pantalla blanca / sin UI | `customtkinter` no detectó temas | Incluye `--hidden-import customtkinter` en `build.py` |

---

## 5. Distribución

### Opción A: ZIP portable (más rápido)

Comprime toda la carpeta `dist/BacilosApp/` en un `.zip`. El usuario solo descomprime y ejecuta.

**Ventaja:** Fácil, sin permisos de administrador.  
**Desventaja:** No crea accesos directos ni menú Inicio.

> **Token RENIEC:** coloca el archivo `.env` dentro de `dist/BacilosApp/` (junto al `.exe`) antes de comprimir, o instruye al usuario para que lo cree en `%LOCALAPPDATA%\BacilosApp\.env`.

### Opción B: Instalador con Inno Setup (recomendado para producción)

1. Descarga e instala [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Abre `installer.iss` (incluido en este proyecto).
3. Compila (Ctrl+F9).
4. Obtendrás `BacilosApp_Setup.exe`.

El instalador:
- Copia la app a `C:\Program Files\BacilosApp\` (o `%LOCALAPPDATA%`).
- Crea acceso directo en el escritorio y menú Inicio.
- Registra la desinstalación en "Agregar o quitar programas".

> **Token RENIEC:** el archivo `.env` puede colocarse en `%LOCALAPPDATA%\BacilosApp\.env` (recomendado, no requiere permisos de admin) o en la carpeta de instalación junto al `.exe`.

---

## 6. Datos del usuario en producción

La aplicación almacena datos mutables en:

```
%LOCALAPPDATA%\BacilosApp\
├── datos.db              ← Base de datos SQLite
├── capturas\             ← Imágenes capturadas/cargadas
├── reportes\             ← PDFs generados
└── bacilos_app.log       ← Logs de la aplicación
```

**Esto significa:**
- Los datos sobreviven reinstalaciones.
- Cada usuario de Windows tiene su propia copia de datos.
- Para backup, simplemente copia `%LOCALAPPDATA%\BacilosApp\datos.db`.

---

## 7. Antivirus y falsos positivos

PyInstaller suele generar falsos positivos en algunos antivirus. Si ocurre:

1. **Firma de código** (recomendado para entornos médicos): adquiere un certificado de firma de código y firma el `.exe` con:
   ```powershell
   signtool sign /f certificado.pfx /p PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 BacilosApp.exe
   ```
2. **Sin certificado:** añade el directorio de la app a las exclusiones del antivirus.
3. **Alternativa:** usa `cx_Freeze` o `Nuitka` en lugar de PyInstaller.

---

## 8. Actualizaciones

Estrategia recomendada:

1. **Base de datos:** nunca sobreescribas `datos.db` durante la actualización. El instalador de Inno Setup puede marcar ese archivo como `onlyifdoesntexist`.
2. **Modelo ML:** si `best.pt` cambia, simplemente reemplaza el archivo en `_internal/modelo/`.
3. **Código:** recompila con `build.py` y redistribuye.

---

## 9. Checklist antes de entregar

- [ ] `python build.py` completado sin errores.
- [ ] `BacilosApp.exe` arranca y muestra login.
- [ ] El token RENIEC está configurado (variable de entorno o `.env`).
- [ ] Se puede registrar un usuario nuevo.
- [ ] Se puede registrar un paciente y consultar RENIEC.
- [ ] La cámara funciona o "Cargar imágenes" permite seleccionar fotos.
- [ ] El procesamiento con YOLO genera resultados y guarda en BD.
- [ ] El PDF se genera correctamente.
- [ ] La carpeta `%LOCALAPPDATA%\BacilosApp\` se crea con `datos.db`, `capturas\`, `reportes\`.
- [ ] Se verificó que el antivirus no bloquea el ejecutable.

---

## 10. Soporte

Si el build falla, revisa:
- `build/BacilosApp/warn-BacilosApp.txt` → módulos faltantes.
- `build/BacilosApp/xref-BacilosApp.html` → dependencias detectadas.
- Consola durante `build.py` → errores de PyInstaller.
