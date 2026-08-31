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
from models import (
    User,
    Order,
    Restaurant,
    Product,
    Address,
    PaymentMethod
)

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
# HEALTH
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'FoodPlease API funcionando'
    }), 200


# ============================================================
# REGISTRO
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

    if not check_password_hash(
        usuario.password,
        password
    ):
        return jsonify({
            'status': 'error',
            'message': 'Correo o contraseña incorrectos'
        }), 401

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
    user_id = int(get_jwt_identity())

    usuario = db.session.get(
        User,
        user_id
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
# EDITAR PERFIL
# ============================================================

@app.route('/api/me', methods=['PUT'])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())

    usuario = db.session.get(
        User,
        user_id
    )

    if not usuario:
        return jsonify({
            'status': 'error',
            'message': 'Usuario no encontrado'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    nombre = data.get(
        'nombre',
        usuario.nombre
    ).strip()

    email = data.get(
        'email',
        usuario.email
    ).strip().lower()

    if not nombre or not email:
        return jsonify({
            'status': 'error',
            'message': 'Nombre y email no pueden estar vacíos'
        }), 400

    email_existente = User.query.filter(
        User.email == email,
        User.id != user_id
    ).first()

    if email_existente:
        return jsonify({
            'status': 'error',
            'message': 'Este correo ya está registrado'
        }), 409

    usuario.nombre = nombre
    usuario.email = email

    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Perfil actualizado correctamente',
        'user': usuario.to_dict()
    }), 200

# ============================================================
# CREAR PEDIDO
# ============================================================

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    required_fields = [
        'restaurante',
        'producto',
        'direccion',
        'metodo_pago',
        'subtotal'
    ]

    for field in required_fields:
        if data.get(field) in [None, '']:
            return jsonify({
                'status': 'error',
                'message': f'El campo {field} es obligatorio'
            }), 400

    subtotal = int(data['subtotal'])
    envio = int(data.get('envio', 1000))
    tarifa_servicio = int(
        data.get('tarifa_servicio', 590)
    )

    total = subtotal + envio + tarifa_servicio

    nuevo_pedido = Order(
        user_id=user_id,
        numero_pedido='TEMP',
        restaurante=data['restaurante'],
        producto=data['producto'],
        cantidad=int(
            data.get('cantidad', 1)
        ),
        adicionales=data.get('adicionales'),
        imagen=data.get('imagen'),
        estado=data.get(
            'estado',
            'confirmado'
        ),
        direccion=data['direccion'],
        metodo_pago=data['metodo_pago'],
        subtotal=subtotal,
        envio=envio,
        tarifa_servicio=tarifa_servicio,
        total=total
    )

    db.session.add(nuevo_pedido)
    db.session.flush()

    nuevo_pedido.numero_pedido = (
        f'FP-{1500 + nuevo_pedido.id}'
    )

    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Pedido creado correctamente',
        'order': nuevo_pedido.to_dict()
    }), 201


# ============================================================
# LISTAR DIRECCIONES DEL USUARIO
# ============================================================

@app.route('/api/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = int(get_jwt_identity())

    direcciones = Address.query.filter_by(
        user_id=user_id
    ).order_by(
        Address.es_principal.desc(),
        Address.id.asc()
    ).all()

    return jsonify({
        'status': 'ok',
        'addresses': [
            direccion.to_dict()
            for direccion in direcciones
        ]
    }), 200


# ============================================================
# CREAR DIRECCION
# ============================================================

@app.route('/api/addresses', methods=['POST'])
@jwt_required()
def create_address():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    nombre = data.get(
        'nombre',
        'Casa'
    ).strip()

    direccion = data.get(
        'direccion',
        ''
    ).strip()

    comuna = data.get(
        'comuna',
        ''
    ).strip()

    referencia = data.get(
        'referencia',
        ''
    ).strip()

    es_principal = data.get(
        'es_principal',
        False
    )

    if not direccion or not comuna:
        return jsonify({
            'status': 'error',
            'message': 'Direccion y comuna son obligatorias'
        }), 400

    # Si será principal, quitamos la marca principal
    # de las otras direcciones del mismo usuario.
    if es_principal:
        Address.query.filter_by(
            user_id=user_id,
            es_principal=True
        ).update({
            'es_principal': False
        })

    nueva_direccion = Address(
        user_id=user_id,
        nombre=nombre,
        direccion=direccion,
        comuna=comuna,
        referencia=referencia,
        es_principal=es_principal
    )

    db.session.add(nueva_direccion)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Direccion creada correctamente',
        'address': nueva_direccion.to_dict()
    }), 201


# ============================================================
# EDITAR DIRECCION
# ============================================================

@app.route(
    '/api/addresses/<int:address_id>',
    methods=['PUT']
)
@jwt_required()
def update_address(address_id):
    user_id = int(get_jwt_identity())

    direccion_usuario = Address.query.filter_by(
        id=address_id,
        user_id=user_id
    ).first()

    if not direccion_usuario:
        return jsonify({
            'status': 'error',
            'message': 'Direccion no encontrada'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    nombre = data.get(
        'nombre',
        direccion_usuario.nombre
    ).strip()

    direccion = data.get(
        'direccion',
        direccion_usuario.direccion
    ).strip()

    comuna = data.get(
        'comuna',
        direccion_usuario.comuna
    ).strip()

    referencia = data.get(
        'referencia',
        direccion_usuario.referencia or ''
    ).strip()

    es_principal = data.get(
        'es_principal',
        direccion_usuario.es_principal
    )

    if not direccion or not comuna:
        return jsonify({
            'status': 'error',
            'message': 'Direccion y comuna son obligatorias'
        }), 400

    if es_principal:
        Address.query.filter(
            Address.user_id == user_id,
            Address.id != address_id
        ).update({
            'es_principal': False
        })

    direccion_usuario.nombre = nombre
    direccion_usuario.direccion = direccion
    direccion_usuario.comuna = comuna
    direccion_usuario.referencia = referencia
    direccion_usuario.es_principal = es_principal

    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Direccion actualizada correctamente',
        'address': direccion_usuario.to_dict()
    }), 200


# ============================================================
# ELIMINAR DIRECCION
# ============================================================

@app.route(
    '/api/addresses/<int:address_id>',
    methods=['DELETE']
)
@jwt_required()
def delete_address(address_id):
    user_id = int(get_jwt_identity())

    direccion_usuario = Address.query.filter_by(
        id=address_id,
        user_id=user_id
    ).first()

    if not direccion_usuario:
        return jsonify({
            'status': 'error',
            'message': 'Direccion no encontrada'
        }), 404

    db.session.delete(direccion_usuario)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Direccion eliminada correctamente'
    }), 200


# ============================================================
# LISTAR METODOS DE PAGO
# ============================================================

@app.route('/api/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    user_id = int(get_jwt_identity())

    metodos = PaymentMethod.query.filter_by(
        user_id=user_id
    ).order_by(
        PaymentMethod.es_principal.desc(),
        PaymentMethod.id.asc()
    ).all()

    return jsonify({
        'status': 'ok',
        'payment_methods': [
            metodo.to_dict()
            for metodo in metodos
        ]
    }), 200


# ============================================================
# CREAR METODO DE PAGO
# ============================================================

@app.route('/api/payment-methods', methods=['POST'])
@jwt_required()
def create_payment_method():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos'
        }), 400

    marca = data.get('marca', '').strip()
    ultimos_4 = data.get('ultimos_4', '').strip()
    es_principal = data.get('es_principal', False)

    if not marca or not ultimos_4:
        return jsonify({
            'status': 'error',
            'message': 'Marca y ultimos 4 digitos son obligatorios'
        }), 400

    if len(ultimos_4) != 4 or not ultimos_4.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Los ultimos 4 digitos no son validos'
        }), 400

    if es_principal:
        PaymentMethod.query.filter_by(
            user_id=user_id,
            es_principal=True
        ).update({
            'es_principal': False
        })

    nuevo_metodo = PaymentMethod(
        user_id=user_id,
        marca=marca,
        ultimos_4=ultimos_4,
        es_principal=es_principal
    )

    db.session.add(nuevo_metodo)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Metodo de pago creado correctamente',
        'payment_method': nuevo_metodo.to_dict()
    }), 201


# ============================================================
# ELIMINAR METODO DE PAGO
# ============================================================

@app.route(
    '/api/payment-methods/<int:payment_method_id>',
    methods=['DELETE']
)
@jwt_required()
def delete_payment_method(payment_method_id):
    user_id = int(get_jwt_identity())

    metodo = PaymentMethod.query.filter_by(
        id=payment_method_id,
        user_id=user_id
    ).first()

    if not metodo:
        return jsonify({
            'status': 'error',
            'message': 'Metodo de pago no encontrado'
        }), 404

    db.session.delete(metodo)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Metodo de pago eliminado correctamente'
    }), 200



# ============================================================
# LISTAR PEDIDOS DEL USUARIO
# ============================================================

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())

    pedidos = Order.query.filter_by(
        user_id=user_id
    ).order_by(
        Order.fecha.desc()
    ).all()

    pedidos_actuales = [
        pedido.to_dict()
        for pedido in pedidos
        if pedido.estado != 'entregado'
    ]

    pedidos_anteriores = [
        pedido.to_dict()
        for pedido in pedidos
        if pedido.estado == 'entregado'
    ]

    return jsonify({
        'status': 'ok',
        'current_orders': pedidos_actuales,
        'previous_orders': pedidos_anteriores
    }), 200


# ============================================================
# DETALLE DE UN PEDIDO
# ============================================================

@app.route(
    '/api/orders/<int:order_id>',
    methods=['GET']
)
@jwt_required()
def get_order_detail(order_id):
    user_id = int(get_jwt_identity())

    pedido = Order.query.filter_by(
        id=order_id,
        user_id=user_id
    ).first()

    if not pedido:
        return jsonify({
            'status': 'error',
            'message': 'Pedido no encontrado'
        }), 404

    return jsonify({
        'status': 'ok',
        'order': pedido.to_dict()
    }), 200

# ============================================================
# LISTAR RESTAURANTES
# ============================================================

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    restaurantes = Restaurant.query.order_by(
        Restaurant.nombre.asc()
    ).all()

    return jsonify({
        'status': 'ok',
        'restaurants': [
            restaurante.to_dict()
            for restaurante in restaurantes
        ]
    }), 200


# ============================================================
# DETALLE DE RESTAURANTE
# ============================================================

@app.route(
    '/api/restaurants/<int:restaurant_id>',
    methods=['GET']
)
def get_restaurant_detail(restaurant_id):
    restaurante = db.session.get(
        Restaurant,
        restaurant_id
    )

    if not restaurante:
        return jsonify({
            'status': 'error',
            'message': 'Restaurante no encontrado'
        }), 404

    return jsonify({
        'status': 'ok',
        'restaurant': restaurante.to_dict()
    }), 200


# ============================================================
# PRODUCTOS DE UN RESTAURANTE
# ============================================================

@app.route(
    '/api/restaurants/<int:restaurant_id>/products',
    methods=['GET']
)
def get_restaurant_products(restaurant_id):
    restaurante = db.session.get(
        Restaurant,
        restaurant_id
    )

    if not restaurante:
        return jsonify({
            'status': 'error',
            'message': 'Restaurante no encontrado'
        }), 404

    productos = Product.query.filter_by(
        restaurant_id=restaurant_id,
        disponible=True
    ).order_by(
        Product.nombre.asc()
    ).all()

    return jsonify({
        'status': 'ok',
        'restaurant': restaurante.to_dict(),
        'products': [
            producto.to_dict()
            for producto in productos
        ]
    }), 200


# ============================================================
# DETALLE DE PRODUCTO
# ============================================================

@app.route(
    '/api/products/<int:product_id>',
    methods=['GET']
)
def get_product_detail(product_id):
    producto = db.session.get(
        Product,
        product_id
    )

    if not producto:
        return jsonify({
            'status': 'error',
            'message': 'Producto no encontrado'
        }), 404

    return jsonify({
        'status': 'ok',
        'product': producto.to_dict()
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