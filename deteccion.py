import cv2
import mediapipe as mp
import numpy as np
import os
import sys
import mediapipe as mp

# Determinar la ruta base: si se ejecuta como .exe, sys._MEIPASS contendrá la ruta temporal
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Construir la ruta al modelo
model_path = os.path.join(BASE_DIR, "mediapipe", "modules", "face_landmark", "face_landmark_front_cpu.binarypb")

# Inicializar MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Variables globales para calibración
CALIBRACION_PITCH = None
CALIBRACION_ROLL = None
CALIBRACION_YAW = None

def calcular_orientacion(landmarks, frame_width, frame_height):
    nariz = landmarks[1]
    menton = landmarks[152]
    ojo_izquierdo = landmarks[33]
    ojo_derecho = landmarks[263]
    oido_izquierdo = landmarks[234]
    oido_derecho = landmarks[454]

    nariz_x, nariz_y = nariz.x * frame_width, nariz.y * frame_height
    menton_x, menton_y = menton.x * frame_width, menton.y * frame_height
    ojo_izquierdo_x, ojo_izquierdo_y = ojo_izquierdo.x * frame_width, ojo_izquierdo.y * frame_height
    ojo_derecho_x, ojo_derecho_y = ojo_derecho.x * frame_width, ojo_derecho.y * frame_height
    oido_izquierdo_x, oido_izquierdo_y = oido_izquierdo.x * frame_width, oido_izquierdo.y * frame_height
    oido_derecho_x, oido_derecho_y = oido_derecho.x * frame_width, oido_derecho.y * frame_height

    vector_vertical = [menton_x - nariz_x, menton_y - nariz_y]
    pitch = np.arctan2(vector_vertical[1], vector_vertical[0]) * (180.0 / np.pi)

    vector_puntos = [nariz_x - ojo_izquierdo_x, nariz_y - ojo_izquierdo_y]  # Relación nariz-ojo
    pitch_ajustado = np.arctan2(vector_puntos[1], vector_puntos[0]) * (180.0 / np.pi)

    vector_lateral = [oido_derecho_x - oido_izquierdo_x, oido_derecho_y - oido_izquierdo_y]
    roll = np.arctan2(vector_lateral[1], vector_lateral[0]) * (180.0 / np.pi)

    vector_horizontal = [ojo_derecho_x - ojo_izquierdo_x, ojo_derecho_y - ojo_izquierdo_y]
    yaw = np.arctan2(vector_horizontal[1], vector_horizontal[0]) * (180.0 / np.pi)

    return pitch_ajustado, roll, yaw

# Función para determinar la dirección de la cabeza
def determinar_direccion(pitch, roll, yaw):
    if CALIBRACION_PITCH is None or CALIBRACION_ROLL is None or CALIBRACION_YAW is None:
        return "Calibrando..."

    pitch_diferencia = abs(pitch - CALIBRACION_PITCH)
    roll_diferencia = abs(roll - CALIBRACION_ROLL)
    yaw_diferencia = abs(yaw - CALIBRACION_YAW)

    # Umbrales de tolerancia ajustados
    if pitch_diferencia <= 5 and roll_diferencia <= 10 and yaw_diferencia <= 30:
        return "Mirando a la pantalla"
    else:
        # Lógica para corregir la postura en el eje YAW
        if yaw_diferencia > 30 or yaw_diferencia < -30:
            return "Corriga la postura"
        else:
            return "Mirando hacia otro lado"

def calcular_atencion(pitch, roll, yaw):
    # Verificar si la calibración se ha realizado
    if CALIBRACION_PITCH is None or CALIBRACION_ROLL is None or CALIBRACION_YAW is None:
        return 0

    # Calcular las diferencias absolutas
    pitch_diferencia = abs(pitch - CALIBRACION_PITCH)
    roll_diferencia = abs(roll - CALIBRACION_ROLL)
    yaw_diferencia = abs(yaw - CALIBRACION_YAW)

    # Penalización ajustada para cada eje
    # Ajusta los factores de multiplicación según la importancia de cada eje
    penalizacion_pitch = max(0, 100 - pitch_diferencia * 5)  # Pitch es más importante
    penalizacion_roll = max(0, 100 - roll_diferencia * 2.5)   # Roll menos importante
    penalizacion_yaw = max(0, 100 - yaw_diferencia * 2.5)     # Yaw menos importante

    # Calcular el nivel de atención como un promedio ponderado
    nivel_atencion = (penalizacion_pitch + penalizacion_roll + penalizacion_yaw) / 3

    # Asegurar que el nivel de atención esté en el rango de 0 a 100
    nivel_atencion = max(0, min(100, nivel_atencion))

    return nivel_atencion

def calibrar_orientacion(pitch, roll, yaw):
    global CALIBRACION_PITCH, CALIBRACION_ROLL, CALIBRACION_YAW
    CALIBRACION_PITCH = pitch
    CALIBRACION_ROLL = roll
    CALIBRACION_YAW = yaw
    print(f"Calibracion completada: Pitch={CALIBRACION_PITCH:.2f}, Roll={CALIBRACION_ROLL:.2f}, Yaw={CALIBRACION_YAW:.2f}")

def dibujar_mascara(frame, landmarks, frame_width, frame_height):
    """
    Dibuja la mascara de puntos en el marco.
    """
    for landmark in landmarks:
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
