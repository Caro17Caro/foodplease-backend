from app import app
from database import db
from models import Restaurant, Product


def upsert_restaurant(
    nombre,
    categoria,
    direccion,
    tiempo_entrega,
    costo_envio,
    calificacion,
    imagen
):
    restaurante = Restaurant.query.filter_by(
        nombre=nombre
    ).first()

    if not restaurante:
        restaurante = Restaurant(
            nombre=nombre
        )
        db.session.add(restaurante)

    restaurante.categoria = categoria
    restaurante.direccion = direccion
    restaurante.tiempo_entrega = tiempo_entrega
    restaurante.costo_envio = costo_envio
    restaurante.calificacion = calificacion
    restaurante.imagen = imagen

    db.session.flush()

    return restaurante


def upsert_product(
    restaurante,
    nombre,
    descripcion,
    precio,
    imagen,
    disponible=True
):
    producto = Product.query.filter_by(
        restaurant_id=restaurante.id,
        nombre=nombre
    ).first()

    if not producto:
        producto = Product(
            restaurant_id=restaurante.id,
            nombre=nombre
        )
        db.session.add(producto)

    producto.descripcion = descripcion
    producto.precio = precio
    producto.imagen = imagen
    producto.disponible = disponible

    return producto


def create_seed():
    with app.app_context():

        # ====================================================
        # LA CASA DE LA HAMBURGUESA
        # ====================================================

        hamburgueseria = upsert_restaurant(
            nombre="La Casa de la Hamburguesa",
            categoria="Hamburguesas",
            direccion="Santiago, Chile",
            tiempo_entrega="25-35 min",
            costo_envio=1000,
            calificacion=4.8,
            imagen="barros_luco.jpeg"
        )

        upsert_product(
            hamburgueseria,
            nombre="Doble carne",
            descripcion="Hamburguesa doble carne con ingredientes seleccionados",
            precio=8400,
            imagen="barros_luco.jpeg"
        )

        upsert_product(
            hamburgueseria,
            nombre="Barros Luco",
            descripcion="Carne y queso fundido",
            precio=5400,
            imagen="barros_luco.jpeg"
        )

        # ====================================================
        # PIZZERIA NAPOLI
        # ====================================================

        napoli = upsert_restaurant(
            nombre="Pizzería Napoli",
            categoria="Pizzas",
            direccion="Santiago, Chile",
            tiempo_entrega="30-40 min",
            costo_envio=1000,
            calificacion=4.7,
            imagen="pizza_napolitana_pesto.jpeg"
        )

        upsert_product(
            napoli,
            nombre="Pizza Burrata - Pesto",
            descripcion="Pizza con burrata, pesto y tomates",
            precio=9400,
            imagen="pizza_napolitana_pesto.jpeg"
        )

        upsert_product(
            napoli,
            nombre="Pizza Burrata",
            descripcion="Pizza artesanal con burrata",
            precio=9900,
            imagen="pizza_burrata.jpeg"
        )

        upsert_product(
            napoli,
            nombre="Pizza Carbonara",
            descripcion="Pizza artesanal estilo carbonara",
            precio=9500,
            imagen="pizza_carbonara.jpeg"
        )

        db.session.commit()

        print("Seed actualizado correctamente.")
        print(
            f"Restaurantes: {Restaurant.query.count()}"
        )
        print(
            f"Productos: {Product.query.count()}"
        )


if __name__ == "__main__":
    create_seed()