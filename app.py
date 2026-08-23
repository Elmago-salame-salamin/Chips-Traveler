# pylint: disable=missing-module-docstring,missing-function-docstring

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# =========================
# CONEXIÓN CON MYSQL
# =========================

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="club_ciencias"
    )


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route('/')
def index():

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # Obtener componentes
    cursor.execute("SELECT * FROM componentes")
    componentes = cursor.fetchall()

    # Obtener préstamos
    consulta_prestamos = """
        SELECT
            p.id_prestamo,
            a.nombre AS alumno_nom,
            a.apellido AS alumno_ape,
            c.nombre AS componente_nom,
            p.fecha_retiro
        FROM prestamos p
        JOIN alumnos a
            ON p.id_alumno = a.dni
        JOIN componentes c
            ON p.id_componente = c.id_componente
    """

    cursor.execute(consulta_prestamos)
    prestamos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'index.html',
        componentes=componentes,
        prestamos=prestamos
    )


# =========================
# NUEVO PRÉSTAMO
# =========================

@app.route('/nuevo_prestamo', methods=['GET', 'POST'])
def nuevo_prestamo():

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # Si se envió el formulario
    if request.method == 'POST':

        dni = request.form['alumno']
        id_comp = request.form['componente']
        fecha = request.form['fecha_retiro']

        # Guardar préstamo
        cursor.execute("""
            INSERT INTO prestamos
            (id_alumno, id_componente, fecha_retiro)
            VALUES (%s, %s, %s)
        """, (dni, id_comp, fecha))

        # Restar 1 al stock
        cursor.execute("""
            UPDATE componentes
            SET stock = stock - 1
            WHERE id_componente = %s
        """, (id_comp,))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('index'))

    # Obtener alumnos
    cursor.execute("""
        SELECT dni, nombre, apellido
        FROM alumnos
    """)
    alumnos = cursor.fetchall()

    # Obtener componentes disponibles
    cursor.execute("""
        SELECT id_componente, nombre
        FROM componentes
        WHERE stock > 0
    """)
    componentes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'prestamo.html',
        alumnos=alumnos,
        componentes=componentes
    )


# =========================
# EJECUTAR APLICACIÓN
# =========================

if __name__ == '__main__':
    app.run(debug=True)
    