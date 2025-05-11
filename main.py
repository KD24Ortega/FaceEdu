# main.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
import cv2
import threading
import time
from PIL import Image, ImageTk
from customtkinter import CTkImage
import sys
import ctypes
import socket
import os
import runpy
#asdasdasdasdasd

# Construir la ruta absoluta al script de dependencias
dependencies_script = os.path.join(os.path.dirname(__file__), "dependencias", "install_dependencies.py")

# Ejecutar el script de dependencias si existe
if os.path.exists(dependencies_script):
    runpy.run_path(dependencies_script)

# Importar funciones de detección
from deteccion import (
    face_mesh,
    calcular_orientacion,
    determinar_direccion,
    calcular_atencion,
    dibujar_mascara,
    calibrar_orientacion
)
from Mysql.db import initialize_database

# Inicializar la base de datos y crear las tablas si no existen
initialize_database()

# Importar el test d2-R (instrucciones)
from test_d2r import InstructionsWindow

# Importar módulos de base de datos para usuarios y sesiones
from Mysql.user_db import obtener_usuarios, registrar_usuario
from Mysql.session_db import guardar_sesion, obtener_sesiones
from Mysql.test_db import obtener_resultados_test


# Configuración de apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def internet_connection_available(host="8.8.8.8", port=53, timeout=3):
    """
    Intenta conectar al servidor DNS de Google para verificar la conexión a internet.
    Retorna True si se establece la conexión, False en caso contrario.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# ============================================================
# Ventana de Login
# ============================================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceEdu - Inicio de Sesión")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.frame = ctk.CTkFrame(self.root, width=450, height=300, corner_radius=15, fg_color="#A04E2C")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Cargar logo
        self.logo_img = Image.open("img/faceedu_logo.png")
        self.logo_img = self.logo_img.resize((50, 50))
        self.logo = CTkImage(light_image=self.logo_img, size=(50, 52))
        self.logo_label = ctk.CTkLabel(self.frame, image=self.logo, text="")
        self.logo_label.place(x=350, y=10)

        self.title_label = ctk.CTkLabel(self.frame, text="Bienvenido a", font=("Helvetica", 24), text_color="white")
        self.title_label.place(x=50, y=25)

        self.title_bold = ctk.CTkLabel(self.frame, text="FaceEdu", font=("Helvetica", 34, "bold"), text_color="#3296d9")
        self.title_bold.place(x=200, y=20)

        self.username_entry = ctk.CTkEntry(self.frame, width=300, height=30, font=("Helvetica", 12),
                                           placeholder_text="Nombre de usuario")
        self.username_entry.place(x=70, y=90)

        self.password_entry = ctk.CTkEntry(self.frame, width=300, height=30, font=("Helvetica", 12),
                                           show="*", placeholder_text="Contraseña")
        self.password_entry.place(x=70, y=130)

        self.login_button = ctk.CTkButton(self.frame, text="Iniciar Sesión", width=250, height=35,
                                          fg_color="white", text_color="black",
                                          font=("Helvetica", 14), command=self.validar_credenciales)
        self.login_button.place(x=100, y=180)

        self.register_button = ctk.CTkButton(self.frame, text="Crear una cuenta", width=250, height=35,
                                             fg_color="#8B3E23", text_color="white",
                                             font=("Helvetica", 14), command=self.abrir_registro)
        self.register_button.place(x=100, y=230)

    def validar_credenciales(self):
        # Verificar conexión a internet antes de continuar
        if not internet_connection_available():
            messagebox.showwarning("Advertencia", "No hay conexión a internet. Por favor, verifica tu conexión e intenta nuevamente.")
            return

        usuario = self.username_entry.get().strip()
        contrasena = self.password_entry.get().strip()

        # Obtener usuarios desde la base de datos
        usuarios = obtener_usuarios()
        if usuario in usuarios and usuarios[usuario] == contrasena:
            messagebox.showinfo("Inicio de Sesión", "Acceso concedido")
            self.root.destroy()
            self.abrir_instrucciones(usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def abrir_registro(self):
        self.root.withdraw()
        root_registro = ctk.CTkToplevel(self.root)
        RegistroWindow(root_registro, self.root)

    def abrir_instrucciones(self, usuario):
        root_instrucciones = ctk.CTk()
        InstruccionesWindow(root_instrucciones, usuario)
        root_instrucciones.mainloop()

# ============================================================
# Ventana de Registro
# ============================================================
class RegistroWindow:
    def __init__(self, root, login_window):
        self.root = root
        self.root.title("Crear Cuenta - FaceEdu")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        self.login_window = login_window

        self.header = ctk.CTkFrame(self.root, width=450, height=50, corner_radius=0, fg_color="#A04E2C")
        self.header.pack(fill="x")

        self.title_label = ctk.CTkLabel(self.header, text="Crear nueva cuenta", font=("Helvetica", 24, "bold"),
                                        text_color="white")
        self.title_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self.root, width=300, height=30, font=("Helvetica", 12),
                                           placeholder_text="Nombre de usuario")
        self.username_entry.place(x=100, y=80)

        self.password_entry = ctk.CTkEntry(self.root, width=300, height=30, font=("Helvetica", 12),
                                           show="*", placeholder_text="Contraseña")
        self.password_entry.place(x=100, y=120)

        self.confirm_password_entry = ctk.CTkEntry(self.root, width=300, height=30, font=("Helvetica", 12),
                                                   show="*", placeholder_text="Repite la Contraseña")
        self.confirm_password_entry.place(x=100, y=160)

        self.register_button = ctk.CTkButton(self.root, text="Crear cuenta", width=250, height=35,
                                             fg_color="#A04E2C", text_color="white",
                                             font=("Helvetica", 14), command=self.registrar_usuario)
        self.register_button.place(x=130, y=210)

        self.exit_button = ctk.CTkButton(self.root, text="Regresar", width=250, height=35,
                                         fg_color="gray", text_color="white",
                                         font=("Helvetica", 14), command=self.regresar_login)
        self.exit_button.place(x=130, y=260)

    def registrar_usuario(self):
        usuario = self.username_entry.get().strip()
        contrasena = self.password_entry.get().strip()
        confirmar_contrasena = self.confirm_password_entry.get().strip()

        if not usuario or not contrasena or not confirmar_contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if contrasena != confirmar_contrasena:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        if registrar_usuario(usuario, contrasena):
            messagebox.showinfo("Registro Exitoso", "Cuenta creada correctamente.")
            self.root.destroy()
            self.login_window.deiconify()
        else:
            messagebox.showerror("Error", "El usuario ya existe o hubo un error.")

    def regresar_login(self):
        self.root.destroy()
        self.login_window.deiconify()

# ============================================================
# Ventana de Instrucciones (Intermedia)
# ============================================================
class InstruccionesWindow:
    def __init__(self, root, usuario, inicial=True):
        self.root = root
        self.usuario = usuario
        self.inicial = inicial
        self.root.title("Instrucciones de Uso - FaceEdu")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.frame = ctk.CTkFrame(self.root, width=550, height=350, corner_radius=10, fg_color="#FAD7B3")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Aprende a usar la aplicación!",
            font=("Helvetica", 20, "bold"),
            text_color="black"
        )
        self.title_label.place(x=20, y=20)

        self.instrucciones_label = ctk.CTkLabel(
            self.frame,
            text=(
                "Instrucciones de uso:\n"
                "  1. Configura tu tiempo de estudio.\n"
                "  2. Sube el PDF que deseas estudiar.\n"
                "  3. Inicia tu sesión de estudio.\n\n"
                "Funcionalidades:\n"
                "  - Detección de atención en tiempo real.\n"
                "  - Resaltado de texto en PDF.\n"
                "  - Temporizador con pausas.\n"
            ),
            font=("Helvetica", 16),
            justify="left",
            text_color="black",
        )
        self.instrucciones_label.place(x=20, y=80)

        if self.inicial:
            self.start_button = ctk.CTkButton(
                self.frame,
                text="Empecemos!",
                fg_color="#8B3E23",
                text_color="white",
                font=("Helvetica", 16, "bold"),
                command=self.abrir_aplicacion_principal
            )
            self.start_button.place(x=200, y=300)
        else:
            self.close_button = ctk.CTkButton(
                self.frame,
                text="Regresar",
                fg_color="#8B3E23",
                text_color="white",
                font=("Helvetica", 16, "bold"),
                command=self.root.destroy
            )
            self.close_button.place(x=200, y=280)

    def abrir_aplicacion_principal(self):
        self.root.destroy()
        root_principal = ctk.CTk()
        VentanaPrincipal(root_principal, self.usuario)
        root_principal.mainloop()

# ============================================================
# Visualizador de PDF
# ============================================================
class PDFViewer(ctk.CTkFrame):
    def __init__(self, parent, pdf_path=None):
        super().__init__(parent, fg_color="white")
        self.pdf_path = pdf_path
        self.doc = None
        self.current_page = 0
        self.scale = 2

        self.is_selecting = False
        self.start_x = self.start_y = 0

        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(self, bg="white",
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set,
                                highlightthickness=0)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)

        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        if pdf_path:
            self.doc = fitz.open(pdf_path)
            self.show_page(self.current_page)

    def show_page(self, page_index):
        if not self.doc:
            return
        if page_index < 0 or page_index >= len(self.doc):
            return

        self.current_page = page_index
        page = self.doc.load_page(page_index)
        zoom_matrix = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=zoom_matrix)

        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

    def go_next(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def go_prev(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def zoom_in(self):
        self.scale += 0.25
        self.show_page(self.current_page)

    def zoom_out(self):
        if self.scale > 0.25:
            self.scale -= 0.25
            self.show_page(self.current_page)

    def on_mouse_down(self, event):
        self.is_selecting = True
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_drag(self, event):
        if not self.is_selecting:
            return
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.canvas.delete("selection_rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y,
                                     outline="red", tag="selection_rect")

    def on_mouse_up(self, event):
        if not self.is_selecting:
            return
        self.is_selecting = False
        self.canvas.delete("selection_rect")
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.create_highlight(self.start_x, self.start_y, end_x, end_y)

    def create_highlight(self, x1, y1, x2, y2):
        if not self.doc:
            return
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        if (x2 - x1) < 5 or (y2 - y1) < 5:
            return

        page = self.doc.load_page(self.current_page)
        scale_inv = 1 / self.scale
        pdf_rect = fitz.Rect(x1 * scale_inv, y1 * scale_inv, x2 * scale_inv, y2 * scale_inv)
        annot = page.add_highlight_annot(pdf_rect)
        if annot:
            annot.update()
        self.show_page(self.current_page)

    def save_pdf(self, output_path=None):
        if not self.doc:
            return
        if not output_path:
            output_path = self.pdf_path
        self.doc.save(output_path, incremental=False, encryption=0)

# ============================================================
# Ventana Principal
# ============================================================
class VentanaPrincipal:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("FaceEdu - Ventana Principal")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        self.tiempo_segundos = None
        self.pdf_path = None

        self.attention_window = None
        self.attention_app = None

        self.header = ctk.CTkFrame(self.root, height=70, fg_color="#A04E2C", corner_radius=0)
        self.header.pack(fill="x")

        self.title_label = ctk.CTkLabel(self.header, text=f"¡Bienvenido, {self.usuario.capitalize()}!",
                        font=("Helvetica", 24, "bold"), text_color="white")
        self.title_label.pack(side="left", padx=20, pady=15)

        self.logout_button = ctk.CTkButton(self.header, text="Cerrar Sesión", fg_color="#8B3E23", text_color="white",
                                           font=("Helvetica", 12), command=self.cerrar_sesion)
        self.logout_button.pack(side="right", padx=20)

        self.main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.main_frame.grid_columnconfigure(0, weight=2, uniform="col_group")
        self.main_frame.grid_columnconfigure(1, weight=2, uniform="col_group")
        self.main_frame.grid_columnconfigure(2, weight=2, uniform="col_group")
        self.main_frame.grid_rowconfigure(0, weight=1, uniform="row_group")
        self.main_frame.grid_rowconfigure(1, weight=1, uniform="row_group")

        # Temporizador
        self.timer_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.timer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.timer_label = ctk.CTkLabel(self.timer_frame, text=" 1. Temporizador", font=("Helvetica", 18, "bold"))
        self.timer_label.pack(pady=5)

        self.time_display = ctk.CTkLabel(self.timer_frame, text="00:00", font=("Helvetica", 24))
        self.time_display.pack(pady=23)

        self.config_timer_button = ctk.CTkButton(self.timer_frame, text="Configurar Tiempo",
                                                 fg_color="#A04E2C", text_color="white",
                                                 font=("Helvetica", 12), command=self.configurar_tiempo)
        self.config_timer_button.pack(pady=5)

        # Subir PDF
        self.upload_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.upload_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.upload_label = ctk.CTkLabel(self.upload_frame, text="2. Subir archivos", font=("Helvetica", 18, "bold"))
        self.upload_label.pack(pady=5)

        image = ctk.CTkImage(light_image=Image.open("img/upload.png"), size=(50, 50))
        self.upload_image_label = ctk.CTkLabel(self.upload_frame, image=image, text="")
        self.upload_image_label.pack(pady=13)

        self.upload_button = ctk.CTkButton(self.upload_frame, text="Seleccionar PDF", fg_color="#A04E2C",
                                           text_color="white", font=("Helvetica", 12), command=self.subir_pdf)
        self.upload_button.pack(pady=5)

        # Iniciar sesión de estudio
        self.study_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.study_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.study_label = ctk.CTkLabel(self.study_frame, text="3. Iniciar Sesión\nde Estudio", font=("Helvetica", 18, "bold"))
        self.study_label.pack(pady=5)

        image = ctk.CTkImage(light_image=Image.open("img/start.png"), size=(40, 40))
        self.start_image_label = ctk.CTkLabel(self.study_frame, image=image, text="")
        self.start_image_label.pack(pady=10)

        self.start_button = ctk.CTkButton(self.study_frame, text="Iniciar", fg_color="#A04E2C", text_color="white",
                                          font=("Helvetica", 12), command=self.iniciar_sesion)
        self.start_button.pack(pady=5)

        # Resumen de sesión
        self.summary_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.summary_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.summary_label = ctk.CTkLabel(self.summary_frame, text="Resumen de Sesión", font=("Helvetica", 18, "bold"))
        self.summary_label.pack(pady=5)

        image = ctk.CTkImage(light_image=Image.open("img/summary.png"), size=(60, 50))
        self.summary_image_label = ctk.CTkLabel(self.summary_frame, image=image, text="")
        self.summary_image_label.pack(pady=10)

        self.summary_button = ctk.CTkButton(self.summary_frame, text="Ver Resumen", fg_color="#A04E2C",
                                            text_color="white", font=("Helvetica", 12), command=self.ver_ultima_sesion)
        self.summary_button.pack(pady=5)

        # Test d2-R
        self.test_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.test_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.test_label = ctk.CTkLabel(self.test_frame, text="Test d2-R", font=("Helvetica", 18, "bold"))
        self.test_label.pack(pady=5)

        image = ctk.CTkImage(light_image=Image.open("img/test.png"), size=(60, 50))
        self.test_image_label = ctk.CTkLabel(self.test_frame, image=image, text="")
        self.test_image_label.pack(pady=10)

        self.test_button = ctk.CTkButton(self.test_frame, text="Iniciar Test d2-R", fg_color="#A04E2C",
                                         text_color="white", font=("Helvetica", 12), command=self.iniciar_test_d2r)
        self.test_button.pack(pady=5)

        # Instrucciones
        self.instructions_frame = ctk.CTkFrame(self.main_frame, fg_color="#FDE4D0", corner_radius=10)
        self.instructions_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.instructions_label = ctk.CTkLabel(self.instructions_frame, text="Ver Instrucciones",
                                               font=("Helvetica", 18, "bold"))
        self.instructions_label.pack(pady=5)

        image = ctk.CTkImage(light_image=Image.open("img/instructions.png"), size=(50, 50))
        self.instructions_image_label = ctk.CTkLabel(self.instructions_frame, image=image, text="")
        self.instructions_image_label.pack(pady=10)

        self.instructions_button = ctk.CTkButton(self.instructions_frame, text="Instrucciones",
                                                 fg_color="#A04E2C", text_color="white",
                                                 font=("Helvetica", 12), command=self.ver_instrucciones)
        self.instructions_button.pack(pady=5)

    def cerrar_sesion(self):
        self.root.destroy()
        nuevo_root = ctk.CTk()
        LoginWindow(nuevo_root)
        nuevo_root.mainloop()

    def ver_instrucciones(self):
        top_instrucciones = ctk.CTkToplevel(self.root)
        InstruccionesWindow(top_instrucciones, self.usuario, inicial=False)
        top_instrucciones.lift()
        top_instrucciones.attributes("-topmost", True)
        top_instrucciones.grab_set()
        top_instrucciones.focus_force()
        top_instrucciones.wait_window()

    def configurar_tiempo(self):
        # (Igual que antes)
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("Configuración del tiempo")
        config_window.geometry("400x300")
        config_window.resizable(False, False)
        config_window.lift()
        config_window.grab_set()

        main_frame = ctk.CTkFrame(config_window, fg_color="#FAD7B3", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text="Configuración del tiempo",
            font=("Helvetica", 18, "bold"),
            text_color="black"
        )
        title_label.pack(pady=(5, 15))

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="#FAD7B3")
        buttons_frame.pack(pady=10)

        btn_25 = ctk.CTkButton(
            buttons_frame,
            text="25:00",
            fg_color="#A04E2C",
            text_color="white",
            width=80,
            command=lambda: self.seleccionar_tiempo_preset(config_window, 25)
        )
        btn_25.grid(row=0, column=0, padx=10, pady=10)

        btn_50 = ctk.CTkButton(
            buttons_frame,
            text="50:00",
            fg_color="#A04E2C",
            text_color="white",
            width=80,
            command=lambda: self.seleccionar_tiempo_preset(config_window, 50)
        )
        btn_50.grid(row=0, column=1, padx=10, pady=10)

        btn_90 = ctk.CTkButton(
            buttons_frame,
            text="90:00",
            fg_color="#A04E2C",
            text_color="white",
            width=80,
            command=lambda: self.seleccionar_tiempo_preset(config_window, 90)
        )
        btn_90.grid(row=1, column=0, padx=10, pady=10)

        btn_personalizar = ctk.CTkButton(
            buttons_frame,
            text="Personalizar",
            fg_color="#A04E2C",
            text_color="white",
            width=80,
            command=lambda: self.abrir_config_personalizada(config_window)
        )
        btn_personalizar.grid(row=1, column=1, padx=10, pady=10)

        cancelar_button = ctk.CTkButton(
            main_frame,
            text="Cancelar",
            fg_color="gray",
            text_color="white",
            width=200,
            command=config_window.destroy
        )
        cancelar_button.pack(pady=(15, 0))

    def seleccionar_tiempo_preset(self, config_window, minutos):
        self.tiempo_segundos = minutos * 60
        self.time_display.configure(text=f"{minutos:02}:00")
        config_window.destroy()

    def abrir_config_personalizada(self, config_window):
        config_window.destroy()
        self.mostrar_ventana_personalizada()

    def mostrar_ventana_personalizada(self):
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("Configuración manual del tiempo")
        config_window.geometry("400x200")
        config_window.resizable(False, False)
        config_window.lift()
        config_window.grab_set()

        main_frame = ctk.CTkFrame(config_window, fg_color="#FAD7B3", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text="Ingrese el tiempo en minutos:",
            font=("Helvetica", 14, "bold"),
            text_color="black"
        )
        title_label.pack(pady=(10, 10))

        self.tiempo_entry = ctk.CTkEntry(
            main_frame,
            width=200,
            height=35,
            font=("Helvetica", 12),
            placeholder_text="Ej: 15"
        )
        self.tiempo_entry.pack()

        button_frame = ctk.CTkFrame(main_frame, fg_color="#FAD7B3")
        button_frame.pack(pady=20)

        guardar_button = ctk.CTkButton(
            button_frame,
            text="Guardar",
            fg_color="#A04E2C",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            command=lambda: self.guardar_tiempo(config_window)
        )
        guardar_button.pack(side="left", padx=10)

        cancelar_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color="gray",
            text_color="white",
            font=("Helvetica", 12),
            command=config_window.destroy
        )
        cancelar_button.pack(side="left", padx=10)

    def guardar_tiempo(self, config_window):
        valor = self.tiempo_entry.get().strip()
        if not valor.isdigit():
            messagebox.showerror("Error", "Por favor, ingresa un número válido de minutos.")
            return

        minutos = int(valor)
        if minutos < 1 or minutos > 240:
            messagebox.showerror("Error", "El tiempo debe estar entre 1 y 240 minutos.")
            return

        self.tiempo_segundos = minutos * 60
        self.time_display.configure(text=f"{minutos:02}:00")
        config_window.destroy()

    def subir_pdf(self):
        ruta_pdf = filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("Archivos PDF", "*.pdf")])
        if ruta_pdf:
            self.pdf_path = ruta_pdf
            messagebox.showinfo("Archivo Seleccionado", f"PDF cargado: {ruta_pdf}")

    def iniciar_sesion(self):
        if self.attention_window is not None and self.attention_window.winfo_exists():
            messagebox.showwarning("Aviso", "La sesión de estudio ya está en curso.")
            return
        if not self.pdf_path:
            messagebox.showwarning("Aviso", "Debes subir un PDF antes de iniciar la sesión.")
            return
        if not self.tiempo_segundos:
            messagebox.showwarning("Aviso", "Primero configura el tiempo.")
            return

        # Ocultar la ventana principal mientras se ejecuta la sesión de atención
        self.root.withdraw()

        self.attention_window = ctk.CTkToplevel(self.root)
        self.attention_window.lift()
        self.attention_window.attributes("-topmost", True)
        # Para que después de 1 segundo se retire el flag "-topmost"
        self.attention_window.after(1000, lambda: self.attention_window.attributes("-topmost", False))

        self.attention_app = AttentionApp(
            self.attention_window,
            self.tiempo_segundos,
            self.pdf_path,
            self.usuario,
            on_close=self.on_attention_app_close
        )

    def on_attention_app_close(self):
        """Se llama cuando cierra la ventana de estudio, para volver a mostrar la principal."""
        self.attention_window = None
        self.attention_app = None
        self.root.deiconify()

    def ver_ultima_sesion(self):
        sesiones = obtener_sesiones(self.usuario)
        texto_resumen = ""
        if sesiones:
            for idx, sesion in enumerate(sesiones, start=1):
                tiempo_estudio = sesion.get("tiempo_estudio", 0)
                distracciones = sesion.get("distracciones", 0)
                minutos, segundos = divmod(tiempo_estudio, 60)
                created_at = sesion.get("created_at", "N/A")
                texto_resumen += (f"Sesión {idx} (Fecha: {created_at}):\n"
                                  f"Tiempo de estudio: {minutos} minutos {segundos} segundos\n"
                                  f"Distracciones: {distracciones}\n\n")
        else:
            texto_resumen += "No hay datos de sesiones anteriores para tu usuario.\n\n"

        # Obtener y mostrar los resultados del test d2‑R
        test_resultado = obtener_resultados_test(self.usuario)
        if test_resultado:
            texto_resumen += "Test d2-R:\n"
            texto_resumen += f"Aciertos: {test_resultado['aciertos']}\n"
            texto_resumen += f"Omisiones: {test_resultado['omisiones']}\n"
            texto_resumen += f"Errores: {test_resultado['errores']}\n"
            texto_resumen += f"Total marcas: {test_resultado['total_marcas']}\n"
            texto_resumen += f"Promedio latencia: {test_resultado['promedio_latencia']:.2f} s\n"
            texto_resumen += f"Fecha: {test_resultado['created_at']}\n"
        else:
            texto_resumen += "No hay datos de test d2-R para tu usuario.\n"

        resumen_window = ctk.CTkToplevel(self.root)
        resumen_window.title("Resumen de la Sesión")
        resumen_window.geometry("400x420")
        resumen_window.resizable(False, False)
        resumen_window.lift()
        resumen_window.grab_set()

        main_frame = ctk.CTkFrame(resumen_window, fg_color="#FAD7B3", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text="Resumen de tus últimas sesiones", font=("Helvetica", 15, "bold"), text_color="black")
        title_label.pack(pady=(5, 10))

        resumen_label = ctk.CTkLabel(main_frame, text=texto_resumen, font=("Helvetica", 12), justify="left", text_color="black")
        resumen_label.pack(pady=10)

        close_button = ctk.CTkButton(main_frame, text="Cerrar", fg_color="#A04E2C", text_color="white", font=("Helvetica", 12), command=resumen_window.destroy)
        close_button.pack(pady=(10, 0))

    def iniciar_test_d2r(self):
        InstructionsWindow(self.root, self.usuario)

# ============================================================
# Aplicación de Atención
# ============================================================
class AttentionApp:
    def __init__(self, root, tiempo_maximo, pdf_path, usuario, on_close=None):
        self.root = root
        self.root.title("Atención al Estudio")
        self.root.configure(bg="#FCE5B7")
        self.root.state("zoomed")
        self.root.resizable(False, False)

        # Forzar que la ventana aparezca siempre al frente
        self.root.lift()
        self.root.attributes("-topmost", True)

        # Bloquear el botón de minimizar (solo en Windows)
        if sys.platform.startswith("win"):
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
            style &= ~0x20000  # WS_MINIMIZEBOX
            style &= ~0x80000  # WS_SYSMENU (This removes the close button)
            ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)

        # Tiempo de estudio elegido
        self.usuario = usuario
        self.pdf_path = pdf_path
        self.tiempo_estudio_inicial = tiempo_maximo
        self.tiempo_restante = tiempo_maximo

        # Descansos según preset
        if tiempo_maximo == 25 * 60:
            self.tiempo_descanso = 5 * 60
        elif tiempo_maximo == 50 * 60:
            self.tiempo_descanso = 10 * 60
        elif tiempo_maximo == 90 * 60:
            self.tiempo_descanso = 15 * 60
        else:
            self.tiempo_descanso = 0

        # Variables de atención
        self.atencion_total = 0
        self.frames_contados = 0
        self.calibrado = False
        self.calibracion_contador = 0
        self.calibracion_duracion = 60
        self.calibracion_pitch = []
        self.calibracion_roll = []
        self.calibracion_yaw = []
        self.distracciones = 0

        self.running = True
        self.timer_paused = False
        self.distraccion_start_time = None
        self.on_close = on_close

        # (MOD) Bandera para saber si estamos en descanso
        self.en_descanso = False

        # Acumulación de tiempo de estudio en varios ciclos
        self.tiempo_estudio_acumulado = 0
        self.inicio_ciclo_estudio = time.time()

        # ---------------------------
        # Interfaz principal
        # ---------------------------
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#FCE5B7", corner_radius=10)
        self.main_frame.pack(fill="both", expand=True)

        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Lado izquierdo: Video, barra y recomendación
        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color="#FCE5B7", corner_radius=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.recomendacion_label = ctk.CTkLabel(
            self.left_frame, text="Recomendación:\nMantén postura y enfócate",
            font=("Helvetica", 16), anchor="w"
        )
        self.recomendacion_label.pack(fill="x", pady=(0, 10))

        self.recommendations = [
            "Mantén postura y enfócate",
            "Recuerda respirar profundamente",
            "Toma descansos breves para estirarte",
            "Establece objetivos para la sesión",
            "Minimiza las distracciones"
        ]
        self.recommendation_index = 0
        self.update_recommendation()

        self.video_frame = ctk.CTkLabel(self.left_frame, text="")
        self.video_frame.pack(pady=5)

        self.bar_frame = ctk.CTkFrame(self.left_frame, fg_color="#FCE5B7", corner_radius=10)
        self.bar_frame.pack(pady=10, fill="x")

        self.canvas = tk.Canvas(self.bar_frame, width=300, height=30, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=5)
        self.rect = self.canvas.create_rectangle(0, 0, 0, 30, fill="green")

        self.porcentaje_label = ctk.CTkLabel(self.bar_frame, text="0.00%", font=("Helvetica", 12))
        self.porcentaje_label.pack(side=tk.LEFT, padx=5)

        self.info_frame = ctk.CTkFrame(self.left_frame, fg_color="#FCE5B7", corner_radius=10)
        self.info_frame.pack(pady=10, fill="x")

        self.estado_label = ctk.CTkLabel(self.info_frame, text="Estado: -", font=("Helvetica", 12))
        self.estado_label.pack(anchor="w", padx=5, pady=3)

        self.timer_label = ctk.CTkLabel(self.info_frame, text="Tiempo: 00:00", font=("Helvetica", 12))
        self.timer_label.pack(anchor="w", padx=5, pady=3)

        self.distraccion_label = ctk.CTkLabel(self.info_frame, text="Distracciones: 0", font=("Helvetica", 12))
        self.distraccion_label.pack(anchor="w", padx=5, pady=3)

        # Lado derecho: PDF Viewer y controles
        self.right_frame = ctk.CTkFrame(self.main_frame, fg_color="#FCE5B7", corner_radius=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.top_bar = ctk.CTkFrame(self.right_frame, fg_color="#FCE5B7", corner_radius=10)
        self.top_bar.pack(side="top", fill="x", padx=5, pady=5)

        self.nav_frame = ctk.CTkFrame(self.top_bar, fg_color="#FCE5B7", corner_radius=10)
        self.nav_frame.pack(side="left")

        self.btn_prev_page = ctk.CTkButton(self.nav_frame, text="<<", width=30, fg_color="#8B3E23", text_color="white",
                                           command=self.go_prev_page)
        self.btn_prev_page.pack(side="left", padx=2)

        self.btn_next_page = ctk.CTkButton(self.nav_frame, text=">>", width=30, fg_color="#8B3E23", text_color="white",
                                           command=self.go_next_page)
        self.btn_next_page.pack(side="left", padx=2)

        self.btn_zoom_out = ctk.CTkButton(self.nav_frame, text="Zoom -", width=30, fg_color="#8B3E23", text_color="white",
                                          command=self.zoom_out_page)
        self.btn_zoom_out.pack(side="left", padx=5)

        self.btn_zoom_in = ctk.CTkButton(self.nav_frame, text="Zoom +", width=30, fg_color="#8B3E23", text_color="white",
                                         command=self.zoom_in_page)
        self.btn_zoom_in.pack(side="left", padx=5)

        self.control_frame = ctk.CTkFrame(self.top_bar, fg_color="#FCE5B7", corner_radius=10)
        self.control_frame.pack(side="right")

        self.btn_exit = ctk.CTkButton(self.control_frame, text="Salir Sesión", fg_color="#8B3E23",
                                      text_color="white", command=self.stop_app)
        self.btn_exit.pack(side="right", padx=3)

        self.btn_save_pdf = ctk.CTkButton(self.control_frame, text="Guardar PDF con Anotaciones", command=self.save_pdf)
        self.btn_save_pdf.pack(side="right", padx=3)

        self.btn_pause = ctk.CTkButton(self.control_frame, text="Pausar Sesion", fg_color="#8B3E23",
                                       text_color="white", command=self.toggle_timer)
        self.btn_pause.pack(side="right", padx=3)

        # PDF Viewer
        self.pdf_viewer = PDFViewer(self.right_frame, pdf_path)
        self.pdf_viewer.pack(side="top", fill="both", expand=True)

        # Iniciar cámara
        self.cap = None
        self.iniciar_video()

        # Iniciar conteo de estudio
        self.start_study_timer(self.tiempo_restante)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Fecha y hora
        self.fecha_hora_label = ctk.CTkLabel(self.main_frame, text="", font=("Helvetica", 12))
        self.fecha_hora_label.grid(row=1, column=1, sticky="se", padx=10, pady=10)
        self.actualizar_fecha_hora()

    # -------------------------------------------------
    # (MOD) Agregar self.en_descanso = True / False
    #       y saltar conteo de distracciones si en_descanso
    # -------------------------------------------------

    def start_study_timer(self, tiempo):
        self.tiempo_restante = tiempo
        self.inicio_ciclo_estudio = time.time()
        self.actualizar_temporizador_estudio()

    def actualizar_temporizador_estudio(self):
        if self.timer_paused:
            self.root.after(1000, self.actualizar_temporizador_estudio)
            return

        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            minutos, segundos = divmod(self.tiempo_restante, 60)
            self.timer_label.configure(text=f"Tiempo: {minutos:02}:{segundos:02}")
            self.root.after(1000, self.actualizar_temporizador_estudio)
        else:
            tiempo_este_ciclo = time.time() - self.inicio_ciclo_estudio
            self.tiempo_estudio_acumulado += tiempo_este_ciclo
            self.estudio_finalizado()

    def estudio_finalizado(self):
        # Si hay tiempo de descanso, lo abrimos
        if self.tiempo_descanso > 0:
            self.mostrar_ventana_descanso(self.tiempo_descanso)
        else:
            self.stop_app()

    def mostrar_ventana_descanso(self, descanso_segundos):
        self.en_descanso = True  # (MOD) Iniciamos descanso
        self.break_window = ctk.CTkToplevel(self.root)
        self.break_window.title("Tiempo de descanso")
        self.break_window.geometry("400x300")
        self.break_window.lift()
        self.break_window.grab_set()

        main_frame = ctk.CTkFrame(self.break_window, fg_color="#FAD7B3", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame, text="Tiempo de descanso",
            font=("Helvetica", 18, "bold"), text_color="black"
        )
        title_label.pack(pady=(5, 15))

        rec_label = ctk.CTkLabel(
            main_frame, text="Recomendaciones:",
            font=("Helvetica", 14, "bold"), text_color="black"
        )
        rec_label.pack()

        self.rec_descanso_label = ctk.CTkLabel(
            main_frame,
            text=self.recommendations[self.recommendation_index],
            font=("Helvetica", 13),
            text_color="black"
        )
        self.rec_descanso_label.pack(pady=5)

        self.break_time_label = ctk.CTkLabel(main_frame, text="", font=("Helvetica", 36, "bold"), text_color="black")
        self.break_time_label.pack(pady=15)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="#FAD7B3")
        btn_frame.pack(pady=(15, 0))

        continuar_btn = ctk.CTkButton(
            btn_frame, text="Continuar",
            fg_color="#A04E2C", text_color="white",
            font=("Helvetica", 14), command=self.interrumpir_descanso
        )
        continuar_btn.grid(row=0, column=0, padx=10)

        finalizar_btn = ctk.CTkButton(
            btn_frame, text="Finalizar",
            fg_color="#A04E2C", text_color="white",
            font=("Helvetica", 14), command=self.finalizar_sesion
        )
        finalizar_btn.grid(row=0, column=1, padx=10)

        self.break_remaining = descanso_segundos
        self.update_break_timer()
        self.break_window.after(20000, self.update_break_recommendation)

    def update_break_timer(self):
        if self.break_remaining <= 0:
            # Se termina el descanso, reiniciamos estudio
            self.break_window.destroy()
            self.en_descanso = False  # (MOD) Fin de descanso
            self.start_study_timer(self.tiempo_estudio_inicial)
            return

        minutos, segundos = divmod(self.break_remaining, 60)
        self.break_time_label.configure(text=f"{minutos}:{segundos:02}")
        self.break_remaining -= 1
        self.break_window.after(1000, self.update_break_timer)

    def update_break_recommendation(self):
        if self.break_window and self.break_window.winfo_exists():
            self.recommendation_index = (self.recommendation_index + 1) % len(self.recommendations)
            self.rec_descanso_label.configure(text=self.recommendations[self.recommendation_index])
            self.break_window.after(20000, self.update_break_recommendation)

    def interrumpir_descanso(self):
        self.break_window.destroy()
        self.en_descanso = False  # (MOD) Fin de descanso
        self.start_study_timer(self.tiempo_estudio_inicial)

    def finalizar_sesion(self):
        self.break_window.destroy()
        self.en_descanso = False  # (MOD) Fin de descanso
        self.stop_app()

    # -------------------------------------------------
    # (MOD) En actualizar_frame, no contamos distracciones si self.en_descanso
    # -------------------------------------------------
    def iniciar_video(self):    
        self.cap = cv2.VideoCapture(0)
        self.actualizar_frame()

    def actualizar_frame(self):
        if not self.running or not self.cap:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            return
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape

            # Llamamos a la detección de rostros
            results = face_mesh.process(frame_rgb)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = face_landmarks.landmark
                    pitch, roll, yaw = calcular_orientacion(landmarks, w, h)
                    if not self.calibrado:
                        self.calibracion_contador += 1
                        self.calibracion_pitch.append(pitch)
                        self.calibracion_roll.append(roll)
                        self.calibracion_yaw.append(yaw)
                        if self.calibracion_contador >= self.calibracion_duracion:
                            avg_pitch = sum(self.calibracion_pitch) / len(self.calibracion_pitch)
                            avg_roll = sum(self.calibracion_roll) / len(self.calibracion_roll)
                            avg_yaw = sum(self.calibracion_yaw) / len(self.calibracion_yaw)
                            calibrar_orientacion(avg_pitch, avg_roll, avg_yaw)
                            self.calibrado = True
                    else:
                        dibujar_mascara(frame, landmarks, w, h)
                        nivel_atencion = calcular_atencion(pitch, roll, yaw)
                        direccion = determinar_direccion(pitch, roll, yaw)

                        # (MOD) Solo contar distracciones si no estamos en descanso
                        if not self.en_descanso:
                            if direccion == "Mirando hacia otro lado":
                                if self.distraccion_start_time is None:
                                    self.distraccion_start_time = time.time()
                                else:
                                    if time.time() - self.distraccion_start_time >= 6:
                                        self.incrementar_distraccion()
                                        self.distraccion_start_time = None
                            else:
                                self.distraccion_start_time = None

                        self.update_bar(nivel_atencion, direccion)
                        self.atencion_total += nivel_atencion
                        self.frames_contados += 1

            img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.video_frame.configure(image=img_tk)
            self.video_frame.image = img_tk

        self.root.after(20, self.actualizar_frame)

    # -------------------------------------------------
    # Zoom, alertas, etc.
    # -------------------------------------------------
    def go_next_page(self):
        self.pdf_viewer.go_next()

    def go_prev_page(self):
        self.pdf_viewer.go_prev()

    def zoom_in_page(self):
        self.pdf_viewer.zoom_in()

    def zoom_out_page(self):
        self.pdf_viewer.zoom_out()

    def save_pdf(self):
        if not self.pdf_viewer.doc:
            return
        save_path = filedialog.asksaveasfilename(title="Guardar PDF", defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
        if save_path:
            self.pdf_viewer.save_pdf(save_path)
            messagebox.showinfo("Guardado", f"PDF guardado en: {save_path}")

    def update_bar(self, value, direction):
        max_width = 300
        fill_width = int((value / 100) * max_width)
        self.canvas.coords(self.rect, 0, 0, fill_width, 30)

        red = int((100 - value) * 2.55)
        green = int(value * 2.55)
        color = f'#{red:02x}{green:02x}00'
        self.canvas.itemconfig(self.rect, fill=color)

        self.estado_label.configure(text=f"Estado: {direction}")
        self.porcentaje_label.configure(text=f"{value:.2f}%")

    def incrementar_distraccion(self):
        self.distracciones += 1
        self.distraccion_label.configure(text=f"Distracciones: {self.distracciones}")

    def toggle_timer(self):
        self.timer_paused = not self.timer_paused
        self.btn_pause.configure(text="Reanudar" if self.timer_paused else "Pausar Sesion")
        if self.timer_paused:
            self.running = False
        else:
            self.running = True
            self.iniciar_video()

    # -------------------------------------------------
    # Finalizar sesión
    # -------------------------------------------------
    def stop_app(self):
        """Finaliza la sesión y regresa a la ventana principal (si on_close está definido)."""
        # Agregamos el tiempo transcurrido del ciclo actual antes de detener la sesión
        if self.inicio_ciclo_estudio is not None:
            tiempo_este_ciclo = time.time() - self.inicio_ciclo_estudio
            self.tiempo_estudio_acumulado += tiempo_este_ciclo
            self.inicio_ciclo_estudio = None

        self.running = False
        self.timer_paused = True

        if self.cap and self.cap.isOpened():
            self.cap.release()

        if self.frames_contados > 0:
            porcentaje_atencion = self.atencion_total / self.frames_contados
        else:
            porcentaje_atencion = 0.0

        total_estudio_segundos = int(self.tiempo_estudio_acumulado)
        guardar_sesion(self.usuario, total_estudio_segundos, self.distracciones, porcentaje_atencion)

        # Mostrar resumen de la sesión
        resumen_window = ctk.CTkToplevel(self.root)
        resumen_window.title("Resumen de la Sesión")
        resumen_window.geometry("400x300")
        resumen_window.lift()
        resumen_window.grab_set()

        main_frame = ctk.CTkFrame(resumen_window, fg_color="#FAD7B3", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text="Sesión Finalizada",
            font=("Helvetica", 15, "bold"),
            text_color="black"
        )
        title_label.pack(pady=(5, 10))

        minutos, segundos = divmod(total_estudio_segundos, 60)
        resumen_text = (
            f"Tiempo total de estudio: {int(minutos)} minutos {int(segundos)} segundos\n"
            f"Distracciones: {self.distracciones}\n"
            f"Porcentaje de atención: {porcentaje_atencion:.2f}%"
        )
        resumen_label = ctk.CTkLabel(
            main_frame,
            text=resumen_text,
            font=("Helvetica", 12),
            justify="left",
            text_color="black"
        )
        resumen_label.pack(pady=10)

        close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            fg_color="#A04E2C",
            text_color="white",
            font=("Helvetica", 12),
            command=lambda: self.cerrar_ventana_estudio(resumen_window)
        )
        close_button.pack(pady=(10, 0))

    # -------------------------------------------------
    # Recomendaciones y hora
    # -------------------------------------------------
    def update_recommendation(self):
        if self.recommendations:
            recommendation_text = self.recommendations[self.recommendation_index]
            self.recomendacion_label.configure(text="Recomendación:\n" + recommendation_text)
            self.recommendation_index = (self.recommendation_index + 1) % len(self.recommendations)

        self.root.after(20000, self.update_recommendation)

    def actualizar_fecha_hora(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.fecha_hora_label.configure(text=now)
        self.root.after(1000, self.actualizar_fecha_hora)
        
    def cerrar_ventana_estudio(self, resumen_window):
        resumen_window.destroy()
        self.root.destroy()
        if self.on_close:
            self.on_close()


# ============================================================
# Bloque Principal de Ejecución
# ============================================================
if __name__ == "__main__":
    root = ctk.CTk()
    LoginWindow(root)
    root.mainloop()
    