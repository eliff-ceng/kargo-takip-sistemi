from app import create_app, db
from app.models import (
    Kargolar,
    Kargo_Hareketleri,
    Subeler,
    Kuryeler,
    Kullanicilar,
    KargoTurleri
)
from datetime import datetime, timedelta
from decimal import Decimal


uygulama = create_app()


with uygulama.app_context():

    # ============================================================
    # KULLANICILAR
    # ============================================================

    kullanicilar = {
        k.kullanici_adi: k
        for k in Kullanicilar.query.all()
    }


    # ============================================================
    # KURYELER
    # ============================================================

    kuryeler = {
        k.kullanici.kullanici_adi: k
        for k in Kuryeler.query.all()
    }


    # ============================================================
    # KARGO TÜRLERİ
    # ============================================================

    kargo_turleri = {
        t.ad: t
        for t in KargoTurleri.query.all()
    }


    # ============================================================
    # ŞUBELER
    # ============================================================

    subeler = {
        s.sube_ad: s
        for s in Subeler.query.all()
    }


    # ============================================================
    # KARGO OLUŞTURMA FONKSİYONU
    # ============================================================

    def kargo_olustur(
        takip_no,
        gonderici_adi,
        alici_adi,
        kargo_turu,
        durum,
        agirlik,
        desi,
        ucret,
        cikis_sube,
        varis_sube,
        kurye_adi,
        gonderim_gun,
        teslim_gun=None
    ):

        gonderici = kullanicilar[gonderici_adi]
        alici = kullanicilar[alici_adi]

        kurye = kuryeler.get(kurye_adi) if kurye_adi else None

        gonderim_tarihi = datetime.now() - timedelta(days=gonderim_gun)

        teslim_tarihi = (
            datetime.now() - timedelta(days=teslim_gun)
            if teslim_gun is not None
            else None
        )

        # Duruma göre kargonun bulunduğu şube
        if durum in ["Teslim Edildi", "Dağıtımda"]:
            mevcut_sube = subeler[varis_sube]
        else:
            mevcut_sube = subeler[cikis_sube]

        return Kargolar(
            takip_no=takip_no,

            # GÖNDERİCİ
            gonderici_id=gonderici.id,
            gonderici=f"{gonderici.ad} {gonderici.soyad}",
            gonderici_telefon=gonderici.telefon,
            gonderici_adres=gonderici.adres,

            # ALICI
            alici_id=alici.id,
            alici=f"{alici.ad} {alici.soyad}",
            alici_telefon=alici.telefon,
            alici_adres=alici.adres,

            # KARGO
            kargo_turu_id=kargo_turleri[kargo_turu].id,
            durum=durum,
            agirlik=Decimal(str(agirlik)),
            desi=Decimal(str(desi)),
            ucret=Decimal(str(ucret)),

            # TARİHLER
            gonderim_tarihi=gonderim_tarihi,
            teslim_tarihi=teslim_tarihi,

            # ŞUBELER
            cikis_sube_id=subeler[cikis_sube].id,
            varis_sube_id=subeler[varis_sube].id,
            sube_id=mevcut_sube.id,

            # KURYE
            kurye_id=kurye.id if kurye else None
        )


    # ============================================================
    # 20 TEST KARGOSU
    # ============================================================

    kargolar = [

        kargo_olustur("KRG100001", "busradeveli", "mustafayalcin", "Standart", "Teslim Edildi", 2.50, 4.00, 120.00, "Isparta Merkez Şubesi", "Konya Selçuklu Şubesi", "merveoflaz", 5, 2),

        kargo_olustur("KRG100002", "mustafayalcin", "senaykaya", "Hızlı Teslimat", "Dağıtımda", 1.20, 2.00, 110.00, "Konya Selçuklu Şubesi", "Ankara Çankaya Şubesi", "suleymandemirel", 2),

        kargo_olustur("KRG100003", "senaykaya", "ardakececi", "Ekspres", "Yolda", 3.75, 6.00, 200.00, "Ankara Çankaya Şubesi", "İstanbul Kadıköy Şubesi", "zehragunes", 3),

        kargo_olustur("KRG100004", "ardakececi", "buraksezer", "Standart", "Şubede", 0.80, 1.50, 70.00, "İstanbul Kadıköy Şubesi", "İzmir Konak Şubesi", "edaerdem", 1),

        kargo_olustur("KRG100005", "buraksezer", "atillailhan", "Hızlı Teslimat", "Dağıtımda", 4.20, 7.00, 205.00, "İzmir Konak Şubesi", "Bursa Osmangazi Şubesi", "bedirhanbulbul", 4),

        kargo_olustur("KRG100006", "atillailhan", "canancandan", "Standart", "Teslim Edildi", 2.10, 4.00, 110.00, "Bursa Osmangazi Şubesi", "İstanbul Kadıköy Şubesi", "tolgasahin", 7, 4),

        kargo_olustur("KRG100007", "canancandan", "volkandemirel", "Hızlı Teslimat", "Dağıtımda", 1.50, 2.50, 120.00, "İstanbul Kadıköy Şubesi", "Adana Seyhan Şubesi", "burcuozberk", 2),

        kargo_olustur("KRG100008", "volkandemirel", "melihguler", "Ekspres", "Yolda", 2.80, 5.00, 185.00, "Adana Seyhan Şubesi", "Eskişehir Odunpazarı Şubesi", "emrekaya", 3),

        kargo_olustur("KRG100009", "melihguler", "leylaunsal", "Standart", "Şubede", 1.00, 2.00, 75.00, "Eskişehir Odunpazarı Şubesi", "Ankara Çankaya Şubesi", "suleymandemirel", 1),

        kargo_olustur("KRG100010", "leylaunsal", "ziyayazici", "Standart", "Teslim Edildi", 2.30, 4.00, 115.00, "Ankara Çankaya Şubesi", "Kayseri Melikgazi Subesi", "selinyildiz", 6, 3),

        kargo_olustur("KRG100011", "ziyayazici", "nazimhikmet", "Hızlı Teslimat", "Dağıtımda", 3.10, 5.00, 165.00, "Kayseri Melikgazi Subesi", "Samsun Atakum Subesi", "onurcelik", 2),

        kargo_olustur("KRG100012", "nazimhikmet", "aysegulyilmaz", "Ekspres", "Teslim Edildi", 5.00, 8.00, 250.00, "Samsun Atakum Subesi", "Isparta Merkez Şubesi", "bengisuozilhan", 7, 4),

        kargo_olustur("KRG100013", "aysegulyilmaz", "miracozer", "Standart", "Dağıtımda", 1.75, 3.00, 90.00, "Isparta Merkez Şubesi", "Antalya Kepez Şubesi", "burakaydin", 1),

        kargo_olustur("KRG100014", "miracozer", "fikrettekin", "Hızlı Teslimat", "Teslim Edildi", 2.60, 4.00, 125.00, "Antalya Kepez Şubesi", "Konya Selçuklu Şubesi", "sedaarslan", 8, 5),

        kargo_olustur("KRG100015", "fikrettekin", "denizkoc", "Hızlı Teslimat", "Dağıtımda", 1.30, 2.50, 110.00, "Konya Selçuklu Şubesi", "Eskişehir Odunpazarı Şubesi", "emrekaya", 2),

        kargo_olustur("KRG100016", "denizkoc", "ecekara", "Standart", "Hazırlanıyor", 0.60, 1.00, 65.00, "Eskişehir Odunpazarı Şubesi", "Bursa Osmangazi Şubesi", None, 0),

        kargo_olustur("KRG100017", "ecekara", "ardakececi", "Hızlı Teslimat", "Dağıtımda", 2.00, 3.00, 125.00, "Bursa Osmangazi Şubesi", "Antalya Kepez Şubesi", "burakaydin", 2),

        kargo_olustur("KRG100018", "ardakececi", "sinemacar", "Ekspres", "Teslim Edildi", 1.10, 2.00, 130.00, "Antalya Kepez Şubesi", "Isparta Merkez Şubesi", "damlakurt", 7, 4),

        kargo_olustur("KRG100019", "sinemacar", "miracozer", "Hızlı Teslimat", "Dağıtımda", 3.50, 6.00, 190.00, "Isparta Davraz Şubesi", "Antalya Merkez Şubesi", "cemileacar", 3),

        kargo_olustur("KRG100020", "ardakececi", "buraksezer", "Ekspres", "Teslim Edildi", 1.90, 3.00, 155.00, "İstanbul Beşiktaş Şubesi", "İzmir Bornova Şubesi", "edaerdem", 9, 6)
    ]


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(kargolar)
    db.session.commit()

    print(f"{len(kargolar)} kargo başarıyla eklendi.")