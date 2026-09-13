from flask import Flask, render_template, request, redirect, url_for
from database import conectar_db

app = Flask(__name__, template_folder="template")


# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    return render_template("home.html")


# ==========================================
# LISTA DE LUGARES
# ==========================================
@app.route("/lugares")
def lugares():
    categoria = request.args.get("categoria", "")
    buscar = request.args.get("buscar", "")

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    # Consulta base
    consulta = """
        SELECT
            id_lugar AS id,
            nombre,
            categoria,
            ubicacion,
            descripcion,
            precio,
            valoracion,
            imagen
        FROM lugares
        WHERE 1=1
    """

    parametros = []

    # Filtro por categoría
    if categoria:
        consulta += " AND categoria = %s"
        parametros.append(categoria.lower())

    # Búsqueda por nombre
    if buscar:
        consulta += " AND nombre LIKE %s"
        parametros.append(f"%{buscar}%")

    consulta += " ORDER BY categoria, nombre"

    cursor.execute(consulta, parametros)

    lugares = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "lugares.html",
        lugares=lugares,
        categoria=categoria,
        buscar=buscar
    )


# ==========================================
# INFORMACIÓN DE UN LUGAR
# ==========================================
@app.route("/lugar/<int:id>")
def lugar(id):
    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_lugar AS id,
            nombre,
            categoria,
            ubicacion,
            descripcion,
            precio,
            valoracion,
            imagen
        FROM lugares
        WHERE id_lugar = %s
    """, (id,))

    lugar = cursor.fetchone()

    cursor.close()
    conexion.close()

    if lugar is None:
        return "Lugar no encontrado.", 404

    return render_template(
        "lugar.html",
        lugar=lugar
    )


# ==========================================
# FORMULARIO DE RESERVA
# ==========================================
@app.route("/reserva/<int:id>")
def reserva(id):
    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_lugar AS id,
            nombre,
            categoria,
            ubicacion,
            descripcion,
            precio,
            valoracion,
            imagen
        FROM lugares
        WHERE id_lugar = %s
    """, (id,))

    lugar = cursor.fetchone()

    cursor.close()
    conexion.close()

    if lugar is None:
        return "Lugar no encontrado.", 404

    return render_template(
        "reserva.html",
        lugar=lugar
    )


# ==========================================
# GUARDAR RESERVA
# ==========================================
@app.route("/reserva/<int:id>", methods=["POST"])
def guardar_reserva(id):
    # Datos enviados desde reserva.html
    id_cliente = request.form.get("id_cliente")
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    telefono = request.form.get("telefono")
    fecha = request.form.get("fecha")
    personas = request.form.get("personas")
    comentario = request.form.get("comentario")

    # Verificación básica
    if not id_cliente or not nombre or not telefono or not fecha:
        return "Faltan datos obligatorios.", 400

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # ------------------------------------------
        # Verificar que el lugar exista
        # ------------------------------------------
        cursor.execute("""
            SELECT id_lugar
            FROM lugares
            WHERE id_lugar = %s
        """, (id,))

        lugar = cursor.fetchone()

        if lugar is None:
            return "Lugar no encontrado.", 404

        # ------------------------------------------
        # Verificar si el cliente ya existe
        # ------------------------------------------
        cursor.execute("""
            SELECT id_cliente
            FROM clientes
            WHERE id_cliente = %s
        """, (id_cliente,))

        cliente = cursor.fetchone()

        # ------------------------------------------
        # Si no existe, crear cliente
        # ------------------------------------------
        if cliente is None:
            cursor.execute("""
                INSERT INTO clientes
                (id_cliente, nombre, telefono, email)
                VALUES (%s, %s, %s, %s)
            """, (
                id_cliente,
                nombre,
                telefono,
                email
            ))

        # ------------------------------------------
        # Si existe, actualizar sus datos
        # ------------------------------------------
        else:
            cursor.execute("""
                UPDATE clientes
                SET nombre = %s,
                    telefono = %s,
                    email = %s
                WHERE id_cliente = %s
            """, (
                nombre,
                telefono,
                email,
                id_cliente
            ))

        # ------------------------------------------
        # Crear la reserva
        # ------------------------------------------
        cursor.execute("""
            INSERT INTO reservas
            (
                id_cliente,
                id_lugar,
                fecha,
                personas,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_cliente,
            id,
            fecha,
            personas if personas else 1,
            comentario
        ))

        conexion.commit()

    except Exception as error:
        conexion.rollback()
        return f"Error al guardar la reserva: {error}", 500

    finally:
        cursor.close()
        conexion.close()

    # Volver a la página del lugar
    return redirect(
        url_for(
            "lugar",
            id=id
        )
    )


# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)