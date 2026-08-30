import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database import db
from models import User


app = Flask(__name__)

CORS(app)


# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodplease.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# ============================================================
# CONFIGURACIÓN JWT
# ============================================================

app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY',
    'foodplease-clave-desarrollo-2026'
)


# ============================================================
# INICIALIZAR EXTENSIONES
# ============================================================

db.init_app(app)

jwt = JWTManager(app)


# ============================================================
# CREAR TABLAS
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# PRUEBA DE API
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'FoodPlease API funcionando'
    }), 200


# ============================================================
# REGISTRO DE USUARIO
# ============================================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not nombre or not email or not password:
        return jsonify({
            'status': 'error',
            'message': 'Nombre, email y contraseña son obligatorios'
        }), 400

    usuario_existente = User.query.filter_by(
        email=email
    ).first()

    if usuario_existente:
        return jsonify({
            'status': 'error',
            'message': 'Ya existe una cuenta con este correo'
        }), 409

    password_segura = generate_password_hash(
        password
    )

    nuevo_usuario = User(
        nombre=nombre,
        email=email,
        password=password_segura
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Usuario registrado correctamente',
        'user': nuevo_usuario.to_dict()
    }), 201


# ============================================================
# LOGIN
# ============================================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({
            'status': 'error',
            'message': 'Email y contraseña son obligatorios'
        }), 400

    usuario = User.query.filter_by(
        email=email
    ).first()

    if not usuario:
        return jsonify({
            'status': 'error',
            'message': 'Correo o contraseña incorrectos'
        }), 401

    password_correcta = check_password_hash(
        usuario.password,
        password
    )

    if not password_correcta:
        return jsonify({
            'status': 'error',
            'message': 'Correo o contraseña incorrectos'
        }), 401

    # El token identifica al usuario por su ID.
    access_token = create_access_token(
        identity=str(usuario.id)
    )

    return jsonify({
        'status': 'ok',
        'message': 'Inicio de sesión correcto',
        'access_token': access_token,
        'user': usuario.to_dict()
    }), 200


# ============================================================
# USUARIO AUTENTICADO
# ============================================================

@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    usuario = db.session.get(
        User,
        int(user_id)
    )

    if not usuario:
        return jsonify({
            'status': 'error',
            'message': 'Usuario no encontrado'
        }), 404

    return jsonify({
        'status': 'ok',
        'user': usuario.to_dict()
    }), 200


# ============================================================
# INICIO
# ============================================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )