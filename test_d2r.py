import time
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
from Mysql.test_db import guardar_resultados_test

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

NUM_FILAS = 14
COLUMNAS_POR_FILA = 57
TIEMPO_POR_FILA = 20

ESTIMULOS_DISPONIBLES = ["d||", "d|", "p||", "p|", "b||", "b|"]

ESTIMULOS_14x57 = []
for _ in range(NUM_FILAS):
    fila = []
    for _ in range(COLUMNAS_POR_FILA):
        fila.append(random.choice(ESTIMULOS_DISPONIBLES))
    ESTIMULOS_14x57.append(fila)

ITEM_CORRECTO = "d||"

class TestD2RApp(ctk.CTkToplevel):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario  # Se guarda el usuario para usarlo al guardar resultados
        self.title("Simulación d2-R Test")
        self.configure(fg_color="#FCE5B7")
        if parent:
            self.transient(parent)
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, self.disable_topmost)
        
        self.current_row = 0
        self.respuestas = []  # Almacena tuplas: (fila, columna, tiempo_click, latencia)
        self.timer_id = None
        self.tiempo_restante = TIEMPO_POR_FILA
        self.row_start_time = None
        self.rect_active = None
        self.test_iniciado = False

        # Parámetros de dibujo de la tabla
        self.x_offset = 20
        self.espaciado = 30
        self.row_spacing = 40
        canvas_width = self.x_offset + COLUMNAS_POR_FILA * self.espaciado + 10
        canvas_height = 60 + NUM_FILAS * self.row_spacing
        
        self.canvas_filas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg="#FCE5B7", highlightthickness=0)
        self.canvas_filas.pack(pady=10)
        
        self.label_tiempo = ctk.CTkLabel(self, text="Tiempo restante: -- s", font=("Arial", 10), fg_color="#FCE5B7")
        self.label_tiempo.pack()
        
        self.btn_cerrar = ctk.CTkButton(self, text="Cerrar Test", command=self.cerrar_test, fg_color="gray", text_color="white")
        self.btn_cerrar.pack(pady=5)
        
        self.dibujar_tabla()
        self.iniciar_prueba()

        # Intercepta el cierre de la ventana (por "X") para guardar los resultados
        self.protocol("WM_DELETE_WINDOW", self.cerrar_test)

    def disable_topmost(self):
        if self.winfo_exists():
            self.attributes("-topmost", False)

    def dibujar_tabla(self):
        # Dibuja el contenido de cada celda en la tabla
        for row in range(NUM_FILAS):
            y_offset = 60 + row * self.row_spacing
            for col, estimulo in enumerate(ESTIMULOS_14x57[row]):
                tag = f"item_{row}_{col}"
                # Se separa la letra de los palitos
                letra = estimulo[0]
                palitos = estimulo[1:]
                texto = f"{palitos}\n{letra}"
                self.canvas_filas.create_text(self.x_offset + col * self.espaciado, y_offset,
                                              text=texto, font=("Courier", 14, "bold"),
                                              fill="black", tags=tag)
                self.canvas_filas.tag_bind(tag, "<Button-1>", self.on_item_click)
        self.dibujar_grid()

    def dibujar_grid(self):
        # Dibuja la cuadrícula sobre el canvas
        y_top = 60 - self.row_spacing / 2
        y_bottom = 60 + (NUM_FILAS - 1) * self.row_spacing + self.row_spacing / 2
        x_left = self.x_offset - self.espaciado / 2
        x_right = self.x_offset + (COLUMNAS_POR_FILA - 1) * self.espaciado + self.espaciado / 2

        # Líneas horizontales
        for row in range(NUM_FILAS + 1):
            y = y_top + row * self.row_spacing
            self.canvas_filas.create_line(x_left, y, x_right, y, fill="black", tags="grid_line")
        # Líneas verticales
        for col in range(COLUMNAS_POR_FILA + 1):
            x = x_left + col * self.espaciado
            self.canvas_filas.create_line(x, y_top, x, y_bottom, fill="black", tags="grid_line")
        self.canvas_filas.tag_lower("grid_line")

    def iniciar_prueba(self):
        self.current_row = 0
        self.respuestas.clear()
        self.tiempo_restante = TIEMPO_POR_FILA
        self.row_start_time = time.time()
        self.test_iniciado = True
        self.update_active_row_highlight()
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.actualizar_tiempo()

    def update_active_row_highlight(self):
        if self.rect_active is not None:
            self.canvas_filas.delete(self.rect_active)
            self.rect_active = None
        y_offset = 60 + self.current_row * self.row_spacing
        rect = self.canvas_filas.create_rectangle(
            0, y_offset - 20,
            self.canvas_filas.winfo_reqwidth(), y_offset + 20,
            fill="#e0e0e0", outline=""
        )
        self.canvas_filas.tag_lower(rect)
        self.rect_active = rect

    def actualizar_tiempo(self):
        self.label_tiempo.configure(
            text=f"Fila activa: {self.current_row+1}    Tiempo restante: {self.tiempo_restante} s"
        )
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.timer_id = self.after(1000, self.actualizar_tiempo)
        else:
            self.current_row += 1
            if self.current_row >= NUM_FILAS:
                self.finalizar_prueba()
                return
            self.tiempo_restante = TIEMPO_POR_FILA
            self.row_start_time = time.time()
            self.update_active_row_highlight()
            self.timer_id = self.after(1000, self.actualizar_tiempo)

    def on_item_click(self, event):
        if not self.test_iniciado:
            return
        # Obtener el ítem clicado a través de su tag
        item_ids = self.canvas_filas.find_withtag("current")
        if not item_ids:
            return
        item = item_ids[0]
        tags = self.canvas_filas.gettags(item)
        row_index = None
        col_index = None
        for t in tags:
            if t.startswith("item_"):
                try:
                    parts = t.split("_")
                    row_index = int(parts[1])
                    col_index = int(parts[2])
                except (IndexError, ValueError):
                    pass
                break
        # Se procesará el clic solo si pertenece a la fila activa
        if row_index is None or row_index != self.current_row:
            return
        # Evitar múltiples clics en la misma celda
        if any(r == row_index and c == col_index for (r, c, _, _) in self.respuestas):
            return
        click_time = time.time()
        latencia = click_time - self.row_start_time if self.row_start_time else 0
        self.respuestas.append((row_index, col_index, click_time, latencia))
        self.canvas_filas.itemconfig(item, fill="red")

    def finalizar_prueba(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        messagebox.showinfo("Fin de la prueba", "¡Has completado el test d2-R!")
        self.calcular_resultados()
        self.test_iniciado = False
        self.cerrar_test()  # Se cierra la ventana tras guardar resultados

    def calcular_resultados(self):
        # Se obtienen las celdas marcadas de forma única
        marcados = {(row, col) for (row, col, _, _) in self.respuestas}
        aciertos = 0
        omisiones = 0
        errores = 0
        for row_idx in range(NUM_FILAS):
            for col_idx, item in enumerate(ESTIMULOS_14x57[row_idx]):
                es_correcto = (item == ITEM_CORRECTO)
                fue_marcado = ((row_idx, col_idx) in marcados)
                if es_correcto and fue_marcado:
                    aciertos += 1
                elif es_correcto and not fue_marcado:
                    omisiones += 1
                elif not es_correcto and fue_marcado:
                    errores += 1
        total_marcas = len(self.respuestas)
        promedio_latencia = (sum(lat for (_, _, _, lat) in self.respuestas) / total_marcas) if total_marcas > 0 else 0
        # Se guardan los resultados junto al usuario
        guardar_resultados_test(self.usuario, aciertos, omisiones, errores, total_marcas, promedio_latencia)

    def cerrar_test(self):
        # Si el test aún está en curso, se calcula y guarda el resultado parcial
        if self.test_iniciado:
            if self.timer_id:
                self.after_cancel(self.timer_id)
            self.calcular_resultados()
            self.test_iniciado = False
        self.destroy()

class InstructionsWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario  # Se pasa el usuario al test
        self.title("Instrucciones Test d2-R")
        self.configure(fg_color="#FCE5B7")
        if parent:
            self.transient(parent)
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, self.disable_topmost)
        instrucciones_texto = (
            "INSTRUCCIONES\n"
            "Se presentan 57 'caracteres' por fila, 14 filas en total.\n"
            f"Cada fila tiene {TIEMPO_POR_FILA} segundos para marcar los ítems.\n"
            "Haz clic únicamente en la fila activa (se resalta en gris claro).\n"
            "Solo se considerarán los ítems 'd||' (correctos).\n"
            "Se calculará un promedio de latencia (tiempo de respuesta).\n\n"
            "Nota: Los palitos se muestran arriba de la letra."
        )
        self.label_instrucciones = ctk.CTkLabel(self, text=instrucciones_texto, font=("Arial", 14, "bold"), fg_color="#FCE5B7")
        self.label_instrucciones.pack(pady=20, padx=20)
        self.btn_comenzar = ctk.CTkButton(self, text="Comenzar Test", command=self.comenzar_test, fg_color="#A04E2C", text_color="white")
        self.btn_comenzar.pack(pady=10)

    def disable_topmost(self):
        if self.winfo_exists():
            self.attributes("-topmost", False)

    def comenzar_test(self):
        # Se inicia el test pasando el usuario
        TestD2RApp(self.master, self.usuario)
        self.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1300x800")
    # Se puede pasar un usuario de prueba, por ejemplo "usuario_prueba"
    InstructionsWindow(root, usuario="usuario_prueba")
    root.mainloop()
