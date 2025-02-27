import mysql.connector

def initialize_database():
    """
    Inicializa la base de datos.
    Como las tablas ya se han creado en Railway, esta función solo verifica
    la conexión a la base de datos.
    """
    try:
        conn = mysql.connector.connect(
            host="shortline.proxy.rlwy.net",
            user="root",
            password="HAEAwZgCnsbtUoGKOLsUCazdowbjZdXK",
            database="faceEdu",  # Si creas una base de datos con otro nombre, cámbialo aquí
            port=22542
        )
        print("Conexión a la base de datos establecida correctamente.")
        conn.close()
    except mysql.connector.Error as err:
        print("Error al conectar a la base de datos:", err)

def get_connection():
    """
    Devuelve una conexión activa a la base de datos en Railway.
    """
    return mysql.connector.connect(
        host="shortline.proxy.rlwy.net",
        user="root",
        password="HAEAwZgCnsbtUoGKOLsUCazdowbjZdXK",
        database="faceEdu",
        port=22542
    )
