# session_db.py
from Mysql.db import get_connection

def guardar_sesion(username, tiempo_estudio, distracciones, porcentaje_atencion):
    """
    Guarda una sesión de estudio en la tabla 'sesiones'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO sesiones (username, tiempo_estudio, distracciones, porcentaje_atencion)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (username, tiempo_estudio, distracciones, porcentaje_atencion))
        conn.commit()
    except Exception as e:
        print("Error al guardar la sesión:", e)
    finally:
        cursor.close()
        conn.close()

def obtener_sesiones(username):
    """
    Recupera las últimas 3 sesiones para el usuario especificado.
    Retorna una lista de diccionarios con los campos de la tabla 'sesiones'.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT tiempo_estudio, distracciones, porcentaje_atencion, created_at
        FROM sesiones
        WHERE username = %s
        ORDER BY created_at DESC
        LIMIT 3
    """
    cursor.execute(query, (username,))
    sesiones = cursor.fetchall()
    cursor.close()
    conn.close()
    return sesiones
