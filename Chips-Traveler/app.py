# Import essential modules from Flask and database connector
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import conectar_db

# Initialize Flask application specifying custom templates directory
app = Flask(__name__, template_folder="template")

# English Comment: Secret key required for managing user sessions securely.
app.secret_key = "traveler_cordoba_secret_key_2026"

# English Comment: Configuration for profile picture upload location and allowed file extensions.
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    """English Comment: Helper function to validate uploaded image extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    """Main route rendering the homepage view."""
    return render_template("home.html")


# ==========================================
# USER MANAGEMENT & AUTHENTICATION ROUTES
# ==========================================

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """English Comment: Render user registration form and process new user accounts with Terms & Conditions check."""
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        acepto_terminos = request.form.get("acepto_terminos")

        # English Comment: Legal verification of Terms and Conditions acceptance.
        if not acepto_terminos:
            flash("Debe aceptar los Términos y Condiciones de Uso para registrarse.")
            return render_template("registro.html")

        if not nombre or not email or not password:
            flash("Todos los campos obligatorios deben ser completados.")
            return render_template("registro.html")

        hashed_password = generate_password_hash(password)

        conexion = conectar_db()
        if conexion is None:
            return "No se pudo conectar con la base de datos.", 500

        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("El correo electrónico ya se encuentra registrado.")
                return render_template("registro.html")

            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, acepto_terminos)
                VALUES (%s, %s, %s, 1)
            """, (nombre, email, hashed_password))

            conexion.commit()
            flash("¡Cuenta creada exitosamente! Por favor inicie sesión.")
            return redirect(url_for("login"))
        except Exception as error:
            conexion.rollback()
            return f"Error al registrar usuario: {error}", 500
        finally:
            cursor.close()
            conexion.close()

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """English Comment: Authenticate existing users and store identity parameters in active session."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conexion = conectar_db()
        if conexion is None:
            return "No se pudo conectar con la base de datos.", 500

        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario and check_password_hash(usuario["password_hash"], password):
            session["usuario_id"] = usuario["id_usuario"]
            session["usuario_nombre"] = usuario["nombre"]
            session["usuario_foto"] = usuario["foto_perfil"]
            return redirect(url_for("home"))
        else:
            flash("Credenciales incorrectas. Verifique su email y contraseña.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """English Comment: Clear current active user session data."""
    session.clear()
    return redirect(url_for("home"))


@app.route("/perfil")
def perfil():
    """English Comment: Display personal user details including bio and avatar."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar_db()
    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (session["usuario_id"],))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template("perfil.html", usuario=usuario)


@app.route("/perfil/editar", methods=["GET", "POST"])
def editar_perfil():
    """English Comment: Allow users to edit profile picture, bio description, and password exclusively from this tab."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar_db()
    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        nueva_password = request.form.get("password")
        foto = request.files.get("foto_perfil")

        nombre_foto = session.get("usuario_foto", "default_avatar.png")

        # English Comment: Process profile picture file upload.
        if foto and allowed_file(foto.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(f"user_{session['usuario_id']}_{foto.filename}")
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nombre_foto = filename
            session["usuario_foto"] = nombre_foto

        if nueva_password and nueva_password.strip() != "":
            hashed_pw = generate_password_hash(nueva_password)
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, descripcion = %s, foto_perfil = %s, password_hash = %s
                WHERE id_usuario = %s
            """, (nombre, descripcion, nombre_foto, hashed_pw, session["usuario_id"]))
        else:
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, descripcion = %s, foto_perfil = %s
                WHERE id_usuario = %s
            """, (nombre, descripcion, nombre_foto, session["usuario_id"]))

        conexion.commit()
        session["usuario_nombre"] = nombre
        cursor.close()
        conexion.close()
        flash("Perfil actualizado correctamente.")
        return redirect(url_for("perfil"))

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (session["usuario_id"],))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template("editar_perfil.html", usuario=usuario)


@app.route("/perfil/eliminar", methods=["POST"])
def eliminar_cuenta():
    """English Comment: Delete current logged-in user account permanently from database."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar_db()
    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (session["usuario_id"],))
    conexion.commit()
    cursor.close()
    conexion.close()

    session.clear()
    flash("Tu cuenta ha sido eliminada permanentemente.")
    return redirect(url_for("home"))


@app.route("/terminos")
def terminos():
    """English Comment: Display mandatory Terms and Conditions of use documentation."""
    return render_template("terminos.html")


# ==========================================
# PLACES LIST
# ==========================================
@app.route("/lugares")
def lugares():
    """Retrieve and filter list of places by category and search keyword."""
    categoria = request.args.get("categoria", "")
    buscar = request.args.get("buscar", "")

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

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

    if categoria:
        consulta += " AND categoria = %s"
        parametros.append(categoria.lower())

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
    id_cliente = request.form.get("id_cliente")
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    telefono = request.form.get("telefono")
    fecha = request.form.get("fecha")
    personas = request.form.get("personas")
    comentario = request.form.get("comentario")

    if not id_cliente or not nombre or not telefono or not fecha:
        return "Faltan datos obligatorios.", 400

    conexion = conectar_db()

    if conexion is None:
        return "No se pudo conectar con la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_lugar
            FROM lugares
            WHERE id_lugar = %s
        """, (id,))

        lugar = cursor.fetchone()

        if lugar is None:
            return "Lugar no encontrado.", 404

        cursor.execute("""
            SELECT id_cliente
            FROM clientes
            WHERE id_cliente = %s
        """, (id_cliente,))

        cliente = cursor.fetchone()

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
    app.run(debug=True)