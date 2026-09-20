from app import create_app, db
from app.models import Kuryeler, Kullanicilar, Subeler, Kargolar

uygulama = create_app()

with uygulama.app_context():

    # ============================================================
    # ÖNEMLİ:
    # Önce KRG100001 - KRG100020 kargolarının kurye bağlantısını
    # kaldırıyoruz.
    # Böylece eski kuryeleri güvenli şekilde silebiliriz.
    # ============================================================

    test_takip_nolari = [
        f"KRG{i:06d}"
        for i in range(1, 21)
    ]

    test_kargolar = Kargolar.query.filter(
        Kargolar.takip_no.in_(test_takip_nolari)
    ).all()

    for kargo in test_kargolar:
        kargo.kurye_id = None

    db.session.commit()

    print("20 test kargosunun kurye bağlantıları kaldırıldı.")


    # ============================================================
    # ESKİ KURYELERİ SİL
    # ============================================================

    eski_kuryeler = Kuryeler.query.all()

    if eski_kuryeler:

        for kurye in eski_kuryeler:
            db.session.delete(kurye)

        db.session.commit()

        print(f"{len(eski_kuryeler)} eski kurye silindi.")
    else:
        print("Silinecek eski kurye bulunamadı.")


    # ============================================================
    # KULLANICILAR
    # ============================================================

    kullanicilar = {
        k.kullanici_adi: k
        for k in Kullanicilar.query.all()
    }


    # ============================================================
    # ŞUBELER
    # ============================================================

    subeler = {
        s.sube_ad: s
        for s in Subeler.query.all()
    }


    # ============================================================
    # GÜNCEL KURYE - ŞUBE EŞLEŞMELERİ
    #
    # Kargolar tablosundaki kurye atamalarıyla uyumludur.
    # ============================================================

    kurye_kullanicilari = {

        # Konya
        "merveoflaz": "Konya Selçuklu Şubesi",
        "sedaarslan": "Konya Selçuklu Şubesi",

        # Ankara
        "suleymandemirel": "Ankara Çankaya Şubesi",

        # İstanbul
        "zehragunes": "İstanbul Kadıköy Şubesi",
        "tolgasahin": "İstanbul Kadıköy Şubesi",

        # İzmir
        "edaerdem": "İzmir Konak Şubesi",

        # Bursa
        "bedirhanbulbul": "Bursa Osmangazi Şubesi",

        # Adana
        "burcuozberk": "Adana Seyhan Şubesi",

        # Eskişehir
        "emrekaya": "Eskişehir Odunpazarı Şubesi",

        # Kayseri
        "selinyildiz": "Kayseri Melikgazi Subesi",

        # Samsun
        "onurcelik": "Samsun Atakum Subesi",

        # Isparta
        "bengisuozilhan": "Isparta Merkez Şubesi",
        "damlakurt": "Isparta Merkez Şubesi",

        # Antalya
        "burakaydin": "Antalya Kepez Şubesi",
        "cemileacar": "Antalya Merkez Şubesi"
    }


    # ============================================================
    # TELEFONLAR
    # ============================================================

    telefonlar = {
        "bengisuozilhan": "05525064578",
        "cemileacar": "05522451785",
        "merveoflaz": "05524885715",
        "zehragunes": "05523564781",
        "edaerdem": "05528889236",
        "bedirhanbulbul": "05524785162",
        "suleymandemirel": "05527885993",
        "burcuozberk": "05525441634",
        "emrekaya": "05526351427",
        "selinyildiz": "05527643891",
        "onurcelik": "05528461573",
        "damlakurt": "05529173846",
        "burakaydin": "05521859463",
        "sedaarslan": "05526742185",
        "tolgasahin": "05523981654"
    }


    # ============================================================
    # YENİ KURYELERİ OLUŞTUR
    # ============================================================

    kurye_listesi = []

    for kullanici_adi, sube_adi in kurye_kullanicilari.items():

        kullanici = kullanicilar.get(kullanici_adi)
        sube = subeler.get(sube_adi)

        if kullanici is None:
            print(
                f"Hata: {kullanici_adi} adlı kullanıcı bulunamadı."
            )
            continue

        if sube is None:
            print(
                f"Hata: {sube_adi} adlı şube bulunamadı."
            )
            continue

        kurye_listesi.append(
            Kuryeler(
                kullanici_id=kullanici.id,
                sube_id=sube.id,
                telefon=telefonlar[kullanici_adi],
                aktif=True
            )
        )


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(kurye_listesi)
    db.session.commit()

    print(
        f"{len(kurye_listesi)} güncel kurye başarıyla eklendi."
    )