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