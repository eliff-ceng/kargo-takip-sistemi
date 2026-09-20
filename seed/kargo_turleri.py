from app import create_app, db
from app.models import KargoTurleri

uygulama = create_app()

with uygulama.app_context():

    kargo_turleri = [
        KargoTurleri(ad="Standart",aciklama="Normal teslimat süresi ile gönderilen kargolar",ek_ucret=0),
        KargoTurleri(ad="Hızlı Teslimat",aciklama="Öncelikli teslimat seçeneği",ek_ucret=25),
        KargoTurleri(ad="Ekspres",aciklama="En hızlı teslimat seçeneği",ek_ucret=50)
    ]

    db.session.add_all(kargo_turleri)
    db.session.commit()

    print("Kargo türleri başarıyla eklendi.")