from app import create_app, db
from app.models import Rol

uygulama = create_app()

with uygulama.app_context():

    roller = [
        Rol(ad="Yönetici"),
        Rol(ad="Şube Personeli"),
        Rol(ad="Kurye"),
        Rol(ad="Müşteri")
    ]

    db.session.add_all(roller)
    db.session.commit()

    print("Roller başarıyla eklendi.")