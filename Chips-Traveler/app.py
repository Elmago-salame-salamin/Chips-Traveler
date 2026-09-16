# Import essential modules from Flask and database connector
from flask import Flask, render_template, request, redirect, url_for
from database import conectar_db

# Initialize Flask application specifying custom templates directory
app = Flask(__name__, template_folder="template")


# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    """Main route rendering the homepage view."""
    return render_template("home.html")


# ==========================================
# PLACES LIST
# ==========================================
@app.route("/lugares")
def lugares():
    """Retrieve and filter list of places by category and search keyword."""
    # Retrieve GET parameters from query string URL
    categoria = request.args.get("categoria", "")
    buscar = request.args.get("buscar", "")

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    # Create dictionary cursor to get results formatted as key-value pairs
    cursor = conexion.cursor(dictionary=True)

    # Base parameterized query to prevent SQL injection vulnerabilities
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

    # Optional category filter
    if categoria:
        consulta += " AND categoria = %s"
        parametros.append(categoria.lower())

    # Partial name search filter
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
# PLACE DETAILS
# ==========================================
@app.route("/lugar/<int:id>")
def lugar(id):
    """Retrieve detailed information for a specific place by ID."""
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
# RESERVATION FORM
# ==========================================
@app.route("/reserva/<int:id>")
def reserva(id):
    """Display the reservation form for a selected place."""
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
# SAVE RESERVATION
# ==========================================
@app.route("/reserva/<int:id>", methods=["POST"])
def guardar_reserva(id):
    """Process POST request, create/update client record, and store reservation."""
    # Extract values sent via form payload body
    id_cliente = request.form.get("id_cliente")
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    telefono = request.form.get("telefono")
    fecha = request.form.get("fecha")
    personas = request.form.get("personas")
    comentario = request.form.get("comentario")

    # Required field verification
    if not id_cliente or not nombre or not telefono or not fecha:
        return "Faltan datos obligatorios.", 400

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        # Check if place exists
        cursor.execute("""
            SELECT id_lugar
            FROM lugares
            WHERE id_lugar = %s
        """, (id,))

        lugar = cursor.fetchone()

        if lugar is None:
            return "Lugar no encontrado.", 404

        # Check if customer already exists
        cursor.execute("""
            SELECT id_cliente
            FROM clientes
            WHERE id_cliente = %s
        """, (id_cliente,))

        cliente = cursor.fetchone()

        # Insert new customer if missing
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

        # Update contact details if customer already exists
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

        # Insert new booking entry
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

        # Commit transactions to persist changes into database
        conexion.commit()

    except Exception as error:
        # Roll back active transaction in case of execution failure
        conexion.rollback()
        return f"Error al guardar la reserva: {error}", 500

    finally:
        # Ensure cursor and database connection are properly closed
        cursor.close()
        conexion.close()

    # Redirect to the booked place details view
    return redirect(
        url_for(
            "lugar",
            id=id
        )
    )

# Ruta: Sobre nosotros
@app.route('/sobre-nosotros')
def sobre_nosotros():
    integrantes = [
        {"nombre": "Eluney Naz", "edad": 17, "rol": "Desarrollador / Integrante"},
        {"nombre": "Benjamín Acosta", "edad": 17, "rol": "Desarrollador / Integrante"},
        {"nombre": "Facundo Salas", "edad": 17, "rol": "Desarrollador / Integrante"},
        {"nombre": "Máximo Oliva", "edad": 16, "rol": "Desarrollador / Integrante"},
        {"nombre": "Máximo Fernández", "edad": 16, "rol": "Desarrollador / Integrante"},
        {"nombre": "Facundo Solano", "edad": 16, "rol": "Desarrollador / Integrante"}
    ]
    return render_template('sobre_nosotros.html', integrantes=integrantes)

# ==========================================
# APPLICATION ENTRYPOINT
# ==========================================
if __name__ == "__main__":
    # Run development server with live reload enabled
    app.run(debug=True)