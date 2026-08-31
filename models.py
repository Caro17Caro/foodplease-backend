from datetime import datetime, timezone

from database import db


# ============================================================
# USUARIO
# ============================================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email
        }


# ============================================================
# DIRECCION
# ============================================================

class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    nombre = db.Column(
        db.String(50),
        nullable=False,
        default='Casa'
    )

    direccion = db.Column(
        db.String(255),
        nullable=False
    )

    comuna = db.Column(
        db.String(100),
        nullable=False
    )

    referencia = db.Column(
        db.String(255),
        nullable=True
    )

    es_principal = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'comuna': self.comuna,
            'referencia': self.referencia,
            'es_principal': self.es_principal
        }


# ============================================================
# METODO DE PAGO
# ============================================================

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    marca = db.Column(
        db.String(50),
        nullable=False
    )

    ultimos_4 = db.Column(
        db.String(4),
        nullable=False
    )

    es_principal = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'marca': self.marca,
            'ultimos_4': self.ultimos_4,
            'es_principal': self.es_principal,
            'descripcion': f'{self.marca} •••• {self.ultimos_4}'
        }


# ============================================================
# RESTAURANTE
# ============================================================

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=False
    )

    direccion = db.Column(
        db.String(255),
        nullable=True
    )

    tiempo_entrega = db.Column(
        db.String(50),
        nullable=True
    )

    costo_envio = db.Column(
        db.Integer,
        nullable=False,
        default=1000
    )

    calificacion = db.Column(
        db.Float,
        nullable=False,
        default=4.5
    )

    imagen = db.Column(
        db.String(255),
        nullable=True
    )

    productos = db.relationship(
        'Product',
        backref='restaurant',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'direccion': self.direccion,
            'tiempo_entrega': self.tiempo_entrega,
            'costo_envio': self.costo_envio,
            'calificacion': self.calificacion,
            'imagen': self.imagen
        }


# ============================================================
# PRODUCTO
# ============================================================

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id'),
        nullable=False
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    descripcion = db.Column(
        db.String(255),
        nullable=True
    )

    precio = db.Column(
        db.Integer,
        nullable=False
    )

    imagen = db.Column(
        db.String(255),
        nullable=True
    )

    disponible = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'imagen': self.imagen,
            'disponible': self.disponible
        }


# ============================================================
# PEDIDO
# ============================================================

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    numero_pedido = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    restaurante = db.Column(
        db.String(150),
        nullable=False
    )

    producto = db.Column(
        db.String(150),
        nullable=False
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    adicionales = db.Column(
        db.String(255),
        nullable=True
    )

    imagen = db.Column(
        db.String(255),
        nullable=True
    )

    estado = db.Column(
        db.String(50),
        nullable=False,
        default='confirmado'
    )

    direccion = db.Column(
        db.String(255),
        nullable=False
    )

    metodo_pago = db.Column(
        db.String(100),
        nullable=False
    )

    subtotal = db.Column(
        db.Integer,
        nullable=False
    )

    envio = db.Column(
        db.Integer,
        nullable=False,
        default=1000
    )

    tarifa_servicio = db.Column(
        db.Integer,
        nullable=False,
        default=590
    )

    total = db.Column(
        db.Integer,
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'numero_pedido': self.numero_pedido,
            'restaurante': self.restaurante,
            'producto': self.producto,
            'cantidad': self.cantidad,
            'adicionales': self.adicionales,
            'imagen': self.imagen,
            'estado': self.estado,
            'direccion': self.direccion,
            'metodo_pago': self.metodo_pago,
            'subtotal': self.subtotal,
            'envio': self.envio,
            'tarifa_servicio': self.tarifa_servicio,
            'total': self.total,
            'fecha': self.fecha.isoformat()
        }