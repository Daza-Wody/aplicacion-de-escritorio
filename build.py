#!/usr/bin/env python3
"""
Script de build para producción.
Genera un ejecutable standalone con PyInstaller en modo --onedir.

Uso:
    python build.py

Requisitos:
    pip install pyinstaller
"""
import os
import sys
import shutil
import subprocess

APP_NAME = "BacilosApp"
ENTRY_POINT = "main.py"
ICON = "assets/bacilos.ico"

# Archivos/carpetas a empaquetar dentro del bundle (lectura solamente)
# Formato: "origen;destino_dentro_del_bundle"
ADD_DATA = [
    "assets;assets",
    "modelo;modelo",
]

# Módulos que PyInstaller podría no detectar automáticamente
HIDDEN_IMPORTS = [
    "ultralytics",
    "ultralytics.nn.modules",
    "ultralytics.utils",
    "cv2",
    "PIL",
    "PIL._imagingtk",
    "PIL._tkinter_finder",
    "reportlab",
    "requests",
    "customtkinter",
    "darkdetect",
    "utils.paths",
    "utils.config",
    "utils.remember",
    "views.historial_view",
]


def clean():
    """Elimina artefactos de builds anteriores."""
    dirs_to_remove = ["build", "dist", f"{APP_NAME}.spec"]
    for name in dirs_to_remove:
        if os.path.exists(name):
            print(f"[CLEAN] Eliminando {name} ...")
            shutil.rmtree(name, ignore_errors=True)


def build():
    """Ejecuta PyInstaller."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",          # Sin consola (GUI)
        "--onedir",            # Directorio en lugar de .exe único (mejor para ML grandes)
        "--icon", ICON,
        "--noconfirm",
        "--clean",
    ]

    for item in ADD_DATA:
        cmd += ["--add-data", item]

    for mod in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", mod]

    # Evitar que antivirus marquen el bootloader (opcional pero recomendado)
    # cmd += ["--noupx"]  # Descomenta si el antivirus bloquea el .exe

    cmd.append(ENTRY_POINT)

    print("[BUILD] Ejecutando PyInstaller ...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, check=False)

    if result.returncode != 0:
        print("[ERROR] PyInstaller falló.")
        sys.exit(1)

    print(f"[BUILD] Build completado en: dist/{APP_NAME}/")


def verify():
    """Verifica que el ejecutable y los recursos estén presentes."""
    exe_path = os.path.join("dist", APP_NAME, f"{APP_NAME}.exe")
    assets_dir = os.path.join("dist", APP_NAME, "_internal", "assets")
    modelo_path = os.path.join("dist", APP_NAME, "_internal", "modelo", "best.pt")

    ok = True
    for path, label in [(exe_path, "Ejecutable"), (assets_dir, "Assets"), (modelo_path, "Modelo YOLO")]:
        if os.path.exists(path):
            size = os.path.getsize(path) if os.path.isfile(path) else "-"
            print(f"[VERIFY] {label}: OK ({size} bytes)")
        else:
            print(f"[VERIFY] {label}: FALTANTE ({path})")
            ok = False

    return ok


def print_summary():
    """Muestra resumen y siguiente pasos."""
    dist_dir = os.path.abspath(os.path.join("dist", APP_NAME))
    total_size = 0
    for root, _, files in os.walk(dist_dir):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))

    print("\n" + "=" * 60)
    print("BUILD COMPLETADO")
    print("=" * 60)
    print(f"Directorio: {dist_dir}")
    print(f"Tamaño total: {total_size / (1024*1024):.1f} MB")
    print("\nSiguientes pasos:")
    print("  1. Prueba el ejecutable: dist/BacilosApp/BacilosApp.exe")
    print("  2. Para distribuir, comprime la carpeta dist/BacilosApp en ZIP")
    print("  3. Para más detalles, revisa 'proceso de instalacion.md'")
    print("=" * 60)


def main():
    clean()
    build()
    if verify():
        print_summary()
    else:
        print("[ERROR] Verificación falló. Revisa los logs de PyInstaller.")
        sys.exit(1)


if __name__ == "__main__":
    main()
