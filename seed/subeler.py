from app import create_app, db
from app.models import Subeler

uygulama = create_app()

with uygulama.app_context():

    subeler = [
        Subeler(sube_ad="Isparta Merkez Şubesi", il="Isparta", ilce="Merkez", adres="Kutlubey Mahallesi Atatürk Caddesi No:10 Kat:1 Daire:2", telefon="02462110001", aktif=True),
        Subeler(sube_ad="Isparta Davraz Şubesi", il="Isparta", ilce="Merkez", adres="Davraz Mahallesi 102. Cadde No:15 Kat:1 Daire:1", telefon="02462110002", aktif=True),
        Subeler(sube_ad="Isparta Çünür Şubesi", il="Isparta", ilce="Merkez", adres="Çünür Mahallesi Üniversite Caddesi No:20 Kat:1 Daire:3", telefon="02462110003", aktif=True),

        Subeler(sube_ad="Burdur Merkez Şubesi", il="Burdur", ilce="Merkez", adres="Özgür Mahallesi İnönü Caddesi No:12 Kat:1 Daire:1", telefon="02482110001", aktif=True),

        Subeler(sube_ad="Antalya Merkez Şubesi", il="Antalya", ilce="Muratpaşa", adres="Muratpaşa Mahallesi Atatürk Caddesi No:25 Kat:1 Daire:4", telefon="02422110001", aktif=True),
        Subeler(sube_ad="Antalya Kepez Şubesi", il="Antalya", ilce="Kepez", adres="Kepez Mahallesi Cumhuriyet Caddesi No:30 Kat:1 Daire:2", telefon="02422110002", aktif=True),
        Subeler(sube_ad="Antalya Konyaaltı Şubesi", il="Antalya", ilce="Konyaaltı", adres="Liman Mahallesi Liman Caddesi No:18 Kat:1 Daire:5", telefon="02422110003", aktif=True),

        Subeler(sube_ad="Bursa Osmangazi Şubesi", il="Bursa", ilce="Osmangazi", adres="Osmangazi Mahallesi İnönü Caddesi No:14 Kat:1 Daire:2", telefon="02242110001", aktif=True),
        Subeler(sube_ad="Bursa Nilüfer Şubesi", il="Bursa", ilce="Nilüfer", adres="Görükle Mahallesi İzmir Caddesi No:22 Kat:1 Daire:3", telefon="02242110002", aktif=True),

        Subeler(sube_ad="İstanbul Kadıköy Şubesi", il="İstanbul", ilce="Kadıköy", adres="Feneryolu Mahallesi Bağdat Caddesi No:35 Kat:1 Daire:2", telefon="02162110001", aktif=True),
        Subeler(sube_ad="İstanbul Beşiktaş Şubesi", il="İstanbul", ilce="Beşiktaş", adres="Abbasağa Mahallesi Barbaros Caddesi No:40 Kat:1 Daire:1", telefon="02122110001", aktif=True),
        Subeler(sube_ad="İstanbul Fatih Şubesi", il="İstanbul", ilce="Fatih", adres="Akşemsettin Mahallesi Millet Caddesi No:16 Kat:1 Daire:4", telefon="02122110002", aktif=True),

        Subeler(sube_ad="Ankara Çankaya Şubesi", il="Ankara", ilce="Çankaya", adres="Kızılay Mahallesi Atatürk Bulvarı No:50 Kat:1 Daire:3", telefon="03122110001", aktif=True),
        Subeler(sube_ad="Ankara Keçiören Şubesi", il="Ankara", ilce="Keçiören", adres="Etlik Mahallesi Cumhuriyet Caddesi No:28 Kat:1 Daire:2", telefon="03122110002", aktif=True),

        Subeler(sube_ad="İzmir Konak Şubesi", il="İzmir", ilce="Konak", adres="Alsancak Mahallesi Gazi Bulvarı No:19 Kat:1 Daire:1", telefon="02322110001", aktif=True),
        Subeler(sube_ad="İzmir Bornova Şubesi", il="İzmir", ilce="Bornova", adres="Kazımdirik Mahallesi Üniversite Caddesi No:24 Kat:1 Daire:5", telefon="02322110002", aktif=True),

        Subeler(sube_ad="Adana Seyhan Şubesi", il="Adana", ilce="Seyhan", adres="Reşatbey Mahallesi İnönü Caddesi No:17 Kat:1 Daire:2", telefon="03222110001", aktif=True),

        Subeler(sube_ad="Konya Selçuklu Şubesi", il="Konya", ilce="Selçuklu", adres="Yazır Mahallesi Ankara Caddesi No:32 Kat:1 Daire:3", telefon="03322110001", aktif=True),

        Subeler(sube_ad="Eskişehir Odunpazarı Şubesi", il="Eskişehir", ilce="Odunpazarı", adres="Hoşnudiye Mahallesi Atatürk Caddesi No:21 Kat:1 Daire:2", telefon="02222110001", aktif=True),

        Subeler(sube_ad="Muğla Menteşe Şubesi", il="Muğla", ilce="Menteşe", adres="Orhaniye Mahallesi Cumhuriyet Caddesi No:13 Kat:1 Daire:1", telefon="02522110001", aktif=True)
    ]

    db.session.add_all(subeler)
    db.session.commit()

    print("20 şube başarıyla eklendi.")