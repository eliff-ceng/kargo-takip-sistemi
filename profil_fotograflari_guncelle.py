from app import create_app, db
from app.models import Kullanicilar

uygulama = create_app()

with uygulama.app_context():

    kullanicilar = Kullanicilar.query.all()

    for kullanici in kullanicilar:

        kullanici.profil_fotografi = (
            kullanici.kullanici_adi + "_profil.jpg"
        )

    db.session.commit()

    print(
        f"{len(kullanicilar)} kullanıcının profil fotoğrafı güncellendi."
    )