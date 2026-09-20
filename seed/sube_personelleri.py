from app import create_app, db
from app.models import SubePersonelleri, Kullanicilar, Subeler

uygulama = create_app()

with uygulama.app_context():

    personel_kullanicilari = {
        "isikhanisik": "Isparta Merkez Şubesi",
        "efesarihan": "Isparta Davraz Şubesi",

        "berrinunsal": "Burdur Merkez Şubesi",

        "mehmetertan": "Antalya Merkez Şubesi",
        "tugbaatci": "Antalya Kepez Şubesi",

        "zubeydeerten": "Bursa Osmangazi Şubesi",

        "muratcangok": "İstanbul Kadıköy Şubesi",
        "ahmetgurdal": "İstanbul Beşiktaş Şubesi",

        "seymaozyigit": "Ankara Çankaya Şubesi",

        "deryaaksoy": "İzmir Konak Şubesi"
    }

    telefonlar = {
        "isikhanisik": "05531024567",
        "efesarihan": "05532147892",
        "berrinunsal": "05533451678",
        "mehmetertan": "05534567821",
        "tugbaatci": "05535671284",
        "zubeydeerten": "05536784519",
        "muratcangok": "05537891246",
        "ahmetgurdal": "05538945671",
        "seymaozyigit": "05539872145",
        "deryaaksoy": "05530987654"
    }

    gorevler = {
        "isikhanisik": "Şube Sorumlusu",
        "efesarihan": "Şube Personeli",
        "berrinunsal": "Şube Personeli",
        "mehmetertan": "Şube Sorumlusu",
        "tugbaatci": "Şube Personeli",
        "zubeydeerten": "Şube Personeli",
        "muratcangok": "Şube Sorumlusu",
        "ahmetgurdal": "Şube Personeli",
        "seymaozyigit": "Şube Sorumlusu",
        "deryaaksoy": "Şube Personeli"
    }

    personel_listesi = []

    for kullanici_adi, sube_adi in personel_kullanicilari.items():

        kullanici = Kullanicilar.query.filter_by(
            kullanici_adi=kullanici_adi
        ).first()

        sube = Subeler.query.filter_by(
            sube_ad=sube_adi
        ).first()

        if kullanici is None:
            print(f"Hata: {kullanici_adi} adlı kullanıcı bulunamadı.")
            continue

        if sube is None:
            print(f"Hata: {sube_adi} adlı şube bulunamadı.")
            continue

        personel_listesi.append(
            SubePersonelleri(
                kullanici_id=kullanici.id,
                sube_id=sube.id,
                telefon=telefonlar[kullanici_adi],
                gorev=gorevler[kullanici_adi],
                aktif=True
            )
        )

    db.session.add_all(personel_listesi)
    db.session.commit()

    print(f"{len(personel_listesi)} şube personeli başarıyla eklendi.")