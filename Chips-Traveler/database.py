import mysql.connector
from mysql.connector import Error


def conectar_db():
    """
    Crea y devuelve una conexión con la base de datos MySQL.
    """
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password=" ",
            database="traveler"
        )
        return conexion
    except Error as error:
        print(f"Error al conectar con MySQL: {error}")
        return None