from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__, template_folder='template')

# Configuración de la conexión a MySQL
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Configurar según su usuario de MySQL
        password="1234",  # Configurar según su contraseña
        database="traveler"  # La base de datos del ejercicio anterior
    )


# Ruta principal: Muestra el inventario y los préstamos actuales
@app.route('/')
def index():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # 1. Traer todos los componentes
    cursor.execute("SELECT * FROM componentes")
    componentes = cursor.fetchall()

    # 2. Traer los préstamos uniendo tablas para ver nombres en vez de IDs
    consulta_prestamos = """
    SELECT
        p.id_prestamo,
        a.nombre AS alumno_nom,
        a.apellido AS alumno_ape,
        c.nombre AS componente_nom,
        p.fecha_retiro,
        p.fecha_devolucion
    FROM prestamos p
    JOIN alumnos a ON p.id_alumno = a.dni
    JOIN componentes c ON p.id_componente = c.id_componente
    """

    cursor.execute(consulta_prestamos)
    prestamos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'chips.html',
        componentes=componentes,
        prestamos=prestamos
    )


# Ruta para procesar el formulario de un nuevo préstamo
@app.route('/nuevo_prestamo', methods=['GET', 'POST'])
def nuevo_prestamo():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':

        # Capturamos los datos enviados por el formulario HTML
        dni_alumno = request.form['alumno']
        id_comp = request.form['componente']
        fecha_ret = request.form['fecha_retiro']

        # Insertamos el registro en la base de datos
        query = """
        INSERT INTO prestamos
        (id_alumno, id_componente, fecha_retiro)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (dni_alumno, id_comp, fecha_ret))
        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('index'))

    else:

        # Obtener alumnos
        cursor.execute(
            "SELECT dni, nombre, apellido FROM alumnos"
        )
        alumnos = cursor.fetchall()

        # Obtener componentes con stock
        cursor.execute(
            "SELECT id_componente, nombre FROM componentes WHERE stock > 0"
        )
        componentes = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template(
            'chips_prestamo.html',
            alumnos=alumnos,
            componentes=componentes
        )


if __name__ == '__main__':
    app.run(debug=True)