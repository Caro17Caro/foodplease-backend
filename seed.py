from app import app
from database import db
from models import Restaurant, Product


def create_seed():
    with app.app_context():

        # Evita duplicar los restaurantes si ejecutamos seed.py otra vez
        if Restaurant.query.first():
            print("Ya existen restaurantes en la base de datos.")
            print("No se agregaron datos duplicados.")
            return

        # ====================================================
        # RESTAURANTE 1
        # ====================================================

        hamburgueseria = Restaurant(
            nombre="La Casa de la Hamburguesa",
            categoria="Hamburguesas",
            direccion="Santiago, Chile",
            tiempo_entrega="25-35 min",
            costo_envio=1000,
            calificacion=4.8,
            imagen="barros_luco.jpeg"
        )

        db.session.add(hamburgueseria)
        db.session.flush()

        productos_hamburgueseria = [
            Product(
                restaurant_id=hamburgueseria.id,
                nombre="Doble carne",
                descripcion="Hamburguesa doble carne con ingredientes seleccionados",
                precio=8400,
                imagen="barros_luco.jpeg",
                disponible=True
            ),
            Product(
                restaurant_id=hamburgueseria.id,
                nombre="Barros Luco",
                descripcion="Carne y queso fundido",
                precio=5400,
                imagen="barros_luco.jpeg",
                disponible=True
            )
        ]

        db.session.add_all(productos_hamburgueseria)

        # ====================================================
        # RESTAURANTE 2
        # ====================================================

        napoli = Restaurant(
            nombre="Pizzería Napoli",
            categoria="Pizzas",
            direccion="Santiago, Chile",
            tiempo_entrega="30-40 min",
            costo_envio=1000,
            calificacion=4.7,
            imagen="pizza_napolitana_pesto.jpeg"
        )

        db.session.add(napoli)
        db.session.flush()

        productos_napoli = [
            Product(
                restaurant_id=napoli.id,
                nombre="Pizza Burrata - Pesto",
                descripcion="Pizza con burrata, pesto y tomates",
                precio=9400,
                imagen="pizza_napolitana_pesto.jpeg",
                disponible=True
            ),
            Product(
                restaurant_id=napoli.id,
                nombre="Pizza Burrata",
                descripcion="Pizza artesanal con burrata",
                precio=9900,
                imagen="pizza_burrata.jpeg",
                disponible=True
            ),
            Product(
                restaurant_id=napoli.id,
                nombre="Pizza Carbonara",
                descripcion="Pizza artesanal estilo carbonara",
                precio=9500,
                imagen="pizza_carbonara.jpeg",
                disponible=True
            )
        ]

        db.session.add_all(productos_napoli)

        # ====================================================
        # GUARDAR
        # ====================================================

        db.session.commit()

        print("Datos de prueba creados correctamente.")
        print()
        print("Restaurantes:")
        print(f"- {hamburgueseria.nombre}")
        print(f"- {napoli.nombre}")
        print()
        print("Productos creados: 5")


if __name__ == "__main__":
    create_seed()