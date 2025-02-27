import importlib
import subprocess
import sys

# Diccionario que mapea el nombre del módulo a instalar (pip package)
dependencies = {
    "customtkinter": "customtkinter",
    "fitz": "PyMuPDF",  # Se importa como 'fitz', pero el paquete es 'PyMuPDF'
    "cv2": "opencv-python",
    "PIL": "Pillow",  # Se importa como PIL (Pillow)
    "mysql.connector": "mysql-connector-python",
    "mediapipe": "mediapipe",
    "numpy": "numpy"
}

def install_package(package):
    """Instala un paquete usando pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    for module_name, package_name in dependencies.items():
        try:
            importlib.import_module(module_name)
            print(f"Módulo '{module_name}' ya está instalado.")
        except ImportError:
            print(f"Módulo '{module_name}' no encontrado. Instalando '{package_name}'...")
            install_package(package_name)

if __name__ == "__main__":
    check_and_install_dependencies()
    print("Todos los paquetes requeridos están instalados.")
