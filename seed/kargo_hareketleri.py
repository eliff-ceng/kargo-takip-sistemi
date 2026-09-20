from app import create_app, db
from app.models import Kargolar, Kargo_Hareketleri, Subeler, Kuryeler
from datetime import datetime, timedelta


uygulama = create_app()


with uygulama.app_context():

    # ============================================================
    # ŞUBELER
    # ============================================================

    subeler = {
        s.sube_ad: s
        for s in Subeler.query.all()
    }


    # ============================================================
    # KURYELER
    # ============================================================

    kuryeler = {
        k.kullanici.kullanici_adi: k
        for k in Kuryeler.query.all()
    }


    # ============================================================
    # KARGOLAR
    # ============================================================

    kargolar = {
        k.takip_no: k
        for k in Kargolar.query.all()
    }


    # ============================================================
    # ESKİ HAREKETLERİ SİL
    # Sadece KRG100001 - KRG100020 kargolarına ait hareketler silinir.
    # ============================================================

    test_takip_nolari = [
        f"KRG{i:06d}"
        for i in range(1, 21)
    ]

    test_kargolar = Kargolar.query.filter(
        Kargolar.takip_no.in_(test_takip_nolari)
    ).all()

    test_kargo_idleri = [
        k.id
        for k in test_kargolar
    ]

    if test_kargo_idleri:

        Kargo_Hareketleri.query.filter(
            Kargo_Hareketleri.kargo_id.in_(test_kargo_idleri)
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

        print("Eski test kargo hareketleri silindi.")


    # ============================================================
    # HAREKET OLUŞTURMA FONKSİYONU
    # ============================================================

    def hareket_olustur(takip_no, durum, aciklama, konum, gun_once, sube_adi=None, kurye_adi=None):

        kargo = kargolar[takip_no]

        sube = subeler[sube_adi] if sube_adi else None

        kurye = kuryeler[kurye_adi] if kurye_adi else None

        tarih = datetime.now() - timedelta(days=gun_once)

        return Kargo_Hareketleri(
            kargo_id=kargo.id,
            sube_id=sube.id if sube else None,
            kurye_id=kurye.id if kurye else None,
            durum=durum,
            aciklama=aciklama,
            konum=konum,
            tarih=tarih
        )


    # ============================================================
    # KARGO HAREKETLERİ
    # ============================================================

    hareketler = [

        # 1 - Isparta -> Konya
        # Kurye: Merve Oflaz -> Konya Selçuklu

        hareket_olustur("KRG100001", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "Isparta Merkez Şubesi", 5, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100001", "Şubede", "Kargo Isparta Merkez Şubesine kabul edildi.", "Isparta Merkez Şubesi", 5, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100001", "Yolda", "Kargo Isparta Merkez Şubesinden Konya Selçuklu Şubesine gönderildi.", "Isparta - Konya", 4, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100001", "Dağıtımda", "Kargo Konya Selçuklu Şubesine ulaştı ve kurye tarafından dağıtıma çıkarıldı.", "Konya Selçuklu", 3, "Konya Selçuklu Şubesi", "merveoflaz"),
        hareket_olustur("KRG100001", "Teslim Edildi", "Kargo alıcıya başarıyla teslim edildi.", "Konya Selçuklu", 2, "Konya Selçuklu Şubesi", "merveoflaz"),


        # 2 - Konya -> Ankara
        # Kurye: Süleyman Demirel -> Ankara Çankaya

        hareket_olustur("KRG100002", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "Konya Selçuklu Şubesi", 2, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100002", "Şubede", "Kargo Konya Selçuklu Şubesine kabul edildi.", "Konya Selçuklu Şubesi", 2, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100002", "Yolda", "Kargo Ankara Çankaya Şubesine gönderildi.", "Konya - Ankara", 1, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100002", "Dağıtımda", "Kargo Ankara Çankaya Şubesine ulaştı ve kurye tarafından dağıtıma çıkarıldı.", "Ankara Çankaya", 0, "Ankara Çankaya Şubesi", "suleymandemirel"),


        # 3 - Ankara -> İstanbul
        # Kurye: Zehra Güneş -> İstanbul Kadıköy

        hareket_olustur("KRG100003", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "Ankara Çankaya Şubesi", 3, "Ankara Çankaya Şubesi"),
        hareket_olustur("KRG100003", "Şubede", "Kargo Ankara Çankaya Şubesine kabul edildi.", "Ankara Çankaya Şubesi", 3, "Ankara Çankaya Şubesi"),
        hareket_olustur("KRG100003", "Yolda", "Kargo İstanbul Kadıköy Şubesine doğru yola çıktı.", "Ankara - İstanbul", 0, "Ankara Çankaya Şubesi"),


        # 4 - İstanbul -> İzmir
        # Kurye: Eda Erdem -> İzmir Konak

        hareket_olustur("KRG100004", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "İstanbul Kadıköy Şubesi", 1, "İstanbul Kadıköy Şubesi"),
        hareket_olustur("KRG100004", "Yolda", "Kargo İzmir Konak Şubesine ulaştırılmak üzere yola çıktı.", "İstanbul - İzmir", 0, "İstanbul Kadıköy Şubesi"),
        hareket_olustur("KRG100004", "Şubede", "Kargo İzmir Konak Şubesine ulaştı.", "İzmir Konak Şubesi", 0, "İzmir Konak Şubesi"),


        # 5 - İzmir -> Bursa
        # Kurye: Bedirhan Bülbül -> Bursa Osmangazi

        hareket_olustur("KRG100005", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "İzmir Konak Şubesi", 4, "İzmir Konak Şubesi"),
        hareket_olustur("KRG100005", "Yolda", "Kargo Bursa Osmangazi Şubesine gönderildi.", "İzmir - Bursa", 2, "İzmir Konak Şubesi"),
        hareket_olustur("KRG100005", "Şubede", "Kargo Bursa Osmangazi Şubesine ulaştı.", "Bursa Osmangazi Şubesi", 1, "Bursa Osmangazi Şubesi"),
        hareket_olustur("KRG100005", "Dağıtımda", "Kargo Bursa Osmangazi Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Bursa Osmangazi", 0, "Bursa Osmangazi Şubesi", "bedirhanbulbul"),


        # 6 - Bursa -> İstanbul
        # Kurye: Tolga Şahin -> İstanbul Kadıköy

        hareket_olustur("KRG100006", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "Bursa Osmangazi Şubesi", 7, "Bursa Osmangazi Şubesi"),
        hareket_olustur("KRG100006", "Yolda", "Kargo İstanbul Kadıköy Şubesine gönderildi.", "Bursa - İstanbul", 6, "Bursa Osmangazi Şubesi"),
        hareket_olustur("KRG100006", "Şubede", "Kargo İstanbul Kadıköy Şubesine ulaştı.", "İstanbul Kadıköy Şubesi", 5, "İstanbul Kadıköy Şubesi"),
        hareket_olustur("KRG100006", "Dağıtımda", "Kargo kurye tarafından dağıtıma çıkarıldı.", "İstanbul Kadıköy", 4, "İstanbul Kadıköy Şubesi", "tolgasahin"),
        hareket_olustur("KRG100006", "Teslim Edildi", "Kargo alıcıya teslim edildi.", "İstanbul Kadıköy", 4, "İstanbul Kadıköy Şubesi", "tolgasahin"),


        # 7 - İstanbul -> Adana
        # Kurye: Burcu Özberk -> Adana Seyhan

        hareket_olustur("KRG100007", "Hazırlanıyor", "Kargo hazırlanıyor.", "İstanbul Kadıköy Şubesi", 2, "İstanbul Kadıköy Şubesi"),
        hareket_olustur("KRG100007", "Yolda", "Kargo Adana Seyhan Şubesine gönderildi.", "İstanbul - Adana", 1, "İstanbul Kadıköy Şubesi"),
        hareket_olustur("KRG100007", "Şubede", "Kargo Adana Seyhan Şubesine ulaştı.", "Adana Seyhan Şubesi", 1, "Adana Seyhan Şubesi"),
        hareket_olustur("KRG100007", "Dağıtımda", "Kargo Adana Seyhan Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Adana Seyhan", 0, "Adana Seyhan Şubesi", "burcuozberk"),


        # 8 - Adana -> Eskişehir
        # Kurye: Emre Kaya -> Eskişehir Odunpazarı

        hareket_olustur("KRG100008", "Hazırlanıyor", "Kargo hazırlanıyor.", "Adana Seyhan Şubesi", 3, "Adana Seyhan Şubesi"),
        hareket_olustur("KRG100008", "Yolda", "Kargo Eskişehir Odunpazarı Şubesine doğru yola çıktı.", "Adana - Eskişehir", 1, "Adana Seyhan Şubesi"),
        hareket_olustur("KRG100008", "Yolda", "Kargo Eskişehir yönünde taşımada.", "Eskişehir yolu", 0, "Adana Seyhan Şubesi"),


        # 9 - Eskişehir -> Ankara
        # Kurye: Süleyman Demirel -> Ankara Çankaya

        hareket_olustur("KRG100009", "Hazırlanıyor", "Kargo hazırlanıyor.", "Eskişehir Odunpazarı Şubesi", 1, "Eskişehir Odunpazarı Şubesi"),
        hareket_olustur("KRG100009", "Yolda", "Kargo Ankara Çankaya Şubesine gönderildi.", "Eskişehir - Ankara", 0, "Eskişehir Odunpazarı Şubesi"),
        hareket_olustur("KRG100009", "Şubede", "Kargo Ankara Çankaya Şubesine ulaştı.", "Ankara Çankaya Şubesi", 0, "Ankara Çankaya Şubesi"),


        # 10 - Ankara -> Kayseri
        # Kurye: Selin Yıldız -> Kayseri Melikgazi

        hareket_olustur("KRG100010", "Hazırlanıyor", "Kargo hazırlanıyor.", "Ankara Çankaya Şubesi", 6, "Ankara Çankaya Şubesi"),
        hareket_olustur("KRG100010", "Yolda", "Kargo Kayseri Melikgazi Şubesine gönderildi.", "Ankara - Kayseri", 5, "Ankara Çankaya Şubesi"),
        hareket_olustur("KRG100010", "Şubede", "Kargo Kayseri Melikgazi Şubesine ulaştı.", "Kayseri Melikgazi", 4, "Kayseri Melikgazi Subesi"),
        hareket_olustur("KRG100010", "Dağıtımda", "Kargo Kayseri Melikgazi Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Kayseri Melikgazi", 3, "Kayseri Melikgazi Subesi", "selinyildiz"),
        hareket_olustur("KRG100010", "Teslim Edildi", "Kargo alıcıya teslim edildi.", "Kayseri Melikgazi", 3, "Kayseri Melikgazi Subesi", "selinyildiz"),


        # 11 - Kayseri -> Samsun
        # Kurye: Onur Çelik -> Samsun Atakum

        hareket_olustur("KRG100011", "Hazırlanıyor", "Kargo hazırlanıyor.", "Kayseri Melikgazi Subesi", 2, "Kayseri Melikgazi Subesi"),
        hareket_olustur("KRG100011", "Yolda", "Kargo Samsun Atakum Şubesine gönderildi.", "Kayseri - Samsun", 1, "Kayseri Melikgazi Subesi"),
        hareket_olustur("KRG100011", "Şubede", "Kargo Samsun Atakum Şubesine ulaştı.", "Samsun Atakum", 1, "Samsun Atakum Subesi"),
        hareket_olustur("KRG100011", "Dağıtımda", "Kargo Samsun Atakum Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Samsun Atakum", 0, "Samsun Atakum Subesi", "onurcelik"),


        # 12 - Samsun -> Isparta
        # Kurye: Bengisu Özilhan -> Isparta Merkez

        hareket_olustur("KRG100012", "Hazırlanıyor", "Kargo hazırlanıyor.", "Samsun Atakum Subesi", 7, "Samsun Atakum Subesi"),
        hareket_olustur("KRG100012", "Yolda", "Kargo Isparta Merkez Şubesine gönderildi.", "Samsun - Isparta", 5, "Samsun Atakum Subesi"),
        hareket_olustur("KRG100012", "Şubede", "Kargo Isparta Merkez Şubesine ulaştı.", "Isparta Merkez", 4, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100012", "Dağıtımda", "Kargo Isparta Merkez Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Isparta Merkez", 4, "Isparta Merkez Şubesi", "bengisuozilhan"),
        hareket_olustur("KRG100012", "Teslim Edildi", "Kargo alıcıya teslim edildi.", "Isparta Merkez", 4, "Isparta Merkez Şubesi", "bengisuozilhan"),


        # 13 - Isparta -> Antalya
        # Kurye: Burak Aydın -> Antalya Kepez

        hareket_olustur("KRG100013", "Hazırlanıyor", "Kargo hazırlanıyor.", "Isparta Merkez Şubesi", 1, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100013", "Yolda", "Kargo Antalya Kepez Şubesine gönderildi.", "Isparta - Antalya", 0, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100013", "Şubede", "Kargo Antalya Kepez Şubesine ulaştı.", "Antalya Kepez", 0, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100013", "Dağıtımda", "Kargo Antalya Kepez Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Antalya Kepez", 0, "Antalya Kepez Şubesi", "burakaydin"),


        # 14 - Antalya -> Konya
        # Kurye: Seda Arslan -> Konya Selçuklu

        hareket_olustur("KRG100014", "Hazırlanıyor", "Kargo hazırlanıyor.", "Antalya Kepez Şubesi", 8, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100014", "Yolda", "Kargo Konya Selçuklu Şubesine gönderildi.", "Antalya - Konya", 7, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100014", "Şubede", "Kargo Konya Selçuklu Şubesine ulaştı.", "Konya Selçuklu", 6, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100014", "Dağıtımda", "Kargo Konya Selçuklu Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Konya Selçuklu", 5, "Konya Selçuklu Şubesi", "sedaarslan"),
        hareket_olustur("KRG100014", "Teslim Edildi", "Kargo alıcıya teslim edildi.", "Konya Selçuklu", 5, "Konya Selçuklu Şubesi", "sedaarslan"),


        # 15 - Konya -> Eskişehir
        # Kurye: Emre Kaya -> Eskişehir Odunpazarı

        hareket_olustur("KRG100015", "Hazırlanıyor", "Kargo hazırlanıyor.", "Konya Selçuklu Şubesi", 2, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100015", "Yolda", "Kargo Eskişehir Odunpazarı Şubesine gönderildi.", "Konya - Eskişehir", 1, "Konya Selçuklu Şubesi"),
        hareket_olustur("KRG100015", "Şubede", "Kargo Eskişehir Odunpazarı Şubesine ulaştı.", "Eskişehir Odunpazarı", 1, "Eskişehir Odunpazarı Şubesi"),
        hareket_olustur("KRG100015", "Dağıtımda", "Kargo Eskişehir Odunpazarı Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Eskişehir Odunpazarı", 0, "Eskişehir Odunpazarı Şubesi", "emrekaya"),


        # 16 - Eskişehir -> Bursa
        # Henüz kurye atanmadı

        hareket_olustur("KRG100016", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "Eskişehir Odunpazarı Şubesi", 0, "Eskişehir Odunpazarı Şubesi"),


        # 17 - Bursa -> Antalya
        # Kurye: Burak Aydın -> Antalya Kepez

        hareket_olustur("KRG100017", "Hazırlanıyor", "Kargo hazırlanıyor.", "Bursa Osmangazi Şubesi", 2, "Bursa Osmangazi Şubesi"),
        hareket_olustur("KRG100017", "Yolda", "Kargo Antalya Kepez Şubesine gönderildi.", "Bursa - Antalya", 1, "Bursa Osmangazi Şubesi"),
        hareket_olustur("KRG100017", "Şubede", "Kargo Antalya Kepez Şubesine ulaştı.", "Antalya Kepez", 1, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100017", "Dağıtımda", "Kargo Antalya Kepez Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Antalya Kepez", 0, "Antalya Kepez Şubesi", "burakaydin"),


        # 18 - Antalya -> Isparta
        # Kurye: Damla Kurt -> Isparta Merkez

        hareket_olustur("KRG100018", "Hazırlanıyor", "Kargo hazırlanıyor.", "Antalya Kepez Şubesi", 7, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100018", "Yolda", "Kargo Isparta Merkez Şubesine gönderildi.", "Antalya - Isparta", 6, "Antalya Kepez Şubesi"),
        hareket_olustur("KRG100018", "Şubede", "Kargo Isparta Merkez Şubesine ulaştı.", "Isparta Merkez", 5, "Isparta Merkez Şubesi"),
        hareket_olustur("KRG100018", "Dağıtımda", "Kargo Isparta Merkez Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Isparta Merkez", 4, "Isparta Merkez Şubesi", "damlakurt"),
        hareket_olustur("KRG100018", "Teslim Edildi", "Kargo alıcıya teslim edildi.", "Isparta Merkez", 4, "Isparta Merkez Şubesi", "damlakurt"),


        # 19 - Isparta Davraz -> Antalya Merkez
        # Kurye: Cemile Acar -> Antalya Merkez

        hareket_olustur("KRG100019", "Hazırlanıyor", "Kargo hazırlanıyor.", "Isparta Davraz Şubesi", 3, "Isparta Davraz Şubesi"),
        hareket_olustur("KRG100019", "Yolda", "Kargo Antalya Merkez Şubesine gönderildi.", "Isparta - Antalya", 2, "Isparta Davraz Şubesi"),
        hareket_olustur("KRG100019", "Şubede", "Kargo Antalya Merkez Şubesine ulaştı.", "Antalya Merkez", 1, "Antalya Merkez Şubesi"),
        hareket_olustur("KRG100019", "Dağıtımda", "Kargo Antalya Merkez Şubesinden kurye tarafından dağıtıma çıkarıldı.", "Antalya Merkez", 0, "Antalya Merkez Şubesi", "cemileacar"),


        # 20 - İstanbul Beşiktaş -> İzmir Bornova
        # Kurye: Eda Erdem -> İzmir Konak
        # Aynı şehir olduğu için kurye uygundur.

        hareket_olustur("KRG100020", "Hazırlanıyor", "Kargo gönderici tarafından hazırlanıyor.", "İstanbul Beşiktaş Şubesi", 9, "İstanbul Beşiktaş Şubesi"),
        hareket_olustur("KRG100020", "Yolda", "Kargo İzmir Bornova Şubesine gönderildi.", "İstanbul - İzmir", 8, "İstanbul Beşiktaş Şubesi"),
        hareket_olustur("KRG100020", "Şubede", "Kargo İzmir Bornova Şubesine ulaştı.", "İzmir Bornova", 7, "İzmir Bornova Şubesi"),
        hareket_olustur("KRG100020", "Dağıtımda", "Kargo İzmir bölgesinde kurye tarafından dağıtıma çıkarıldı.", "İzmir", 6, "İzmir Bornova Şubesi", "edaerdem"),
        hareket_olustur("KRG100020", "Teslim Edildi", "Kargo alıcıya başarıyla teslim edildi.", "İzmir Bornova", 6, "İzmir Bornova Şubesi", "edaerdem")
    ]


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(hareketler)
    db.session.commit()

    print(f"{len(hareketler)} kargo hareketi başarıyla eklendi.")