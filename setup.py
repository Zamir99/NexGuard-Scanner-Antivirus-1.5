from cx_Freeze import setup, Executable
import sys

# Dependencias adicionales, si las hay
build_exe_options = {
    "packages": ["os", "tkinter", "PyQt5", "PIL"],  # Añadir los paquetes que tu programa utiliza
    "include_files": [("assets/", "assets")]  # Añadir los recursos que tu programa utiliza
}

# Configuración de la aplicación
setup(
    name="ProyectoAntivirus",
    version="0.1",
    description="Mi aplicación",
    options={"build_exe": build_exe_options},
    executables=[Executable("ProyectoAntivirus.py", base="Win32GUI" if sys.platform == "win32" else None, icon="assets/ico.png")]
)
