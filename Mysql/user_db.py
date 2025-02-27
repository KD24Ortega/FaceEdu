# user_db.py
from Mysql.db import get_connection

def obtener_usuarios():
    """
    Recupera todos los usuarios (username y password) desde la tabla 'usuarios'.
    Retorna un diccionario {username: password}.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, password FROM usuarios")
    usuarios = {row["username"]: row["password"] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return usuarios

def registrar_usuario(username, password):
    """
    Inserta un nuevo usuario en la tabla 'usuarios'.
    Retorna True si la operación fue exitosa, False en caso de error.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()
        success = True
    except Exception as e:
        print("Error al registrar usuario:", e)
        success = False
    finally:
        cursor.close()
        conn.close()
    return success
