# test_db.py
from Mysql.db import get_connection

def guardar_resultados_test(username, aciertos, omisiones, errores, total_marcas, promedio_latencia):
    """
    Guarda los resultados del test d2‑R en la tabla 'test_d2r'.
    Se incluye el campo 'username' para evitar el error de valor nulo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO test_d2r (username, aciertos, omisiones, errores, total_marcas, promedio_latencia)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (username, aciertos, omisiones, errores, total_marcas, promedio_latencia))
        conn.commit()
    except Exception as e:
        print("Error al guardar resultados del test:", e)
    finally:
        cursor.close()
        conn.close()


def obtener_resultados_test(username):
    """
    Recupera el último resultado del test d2-R para el usuario especificado.
    Retorna un diccionario con los campos de la tabla 'test_d2r'.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT aciertos, omisiones, errores, total_marcas, promedio_latencia, created_at
        FROM test_d2r
        WHERE username = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    cursor.execute(query, (username,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado
