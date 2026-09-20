from app import create_app, db
from app.models import Rol, Kullanicilar
from werkzeug.security import generate_password_hash

uygulama = create_app()

with uygulama.app_context():

    yonetici = Rol.query.filter_by(ad="Yönetici").first()
    sube_personeli = Rol.query.filter_by(ad="Şube Personeli").first()
    kurye = Rol.query.filter_by(ad="Kurye").first()
    musteri = Rol.query.filter_by(ad="Müşteri").first()

    kullanicilar = [

        # YÖNETİCİLER

        Kullanicilar(rol_id=yonetici.id, ad="Elif Nur", soyad="Özek", kullanici_adi="elifnurozek", email="elifnur@gmail.com", sifre=generate_password_hash("123456"), telefon="05321234567", adres="Isparta Merkez, Kutlubey Mahallesi, Atatürk Caddesi, No: 18, Daire: 5"),

        Kullanicilar(rol_id=yonetici.id, ad="Kerim", soyad="Şahin", kullanici_adi="kerimsahin", email="kerim@gmail.com", sifre=generate_password_hash("123456"), telefon="05331234568", adres="Ankara Çankaya, Kızılay Mahallesi, Gazi Mustafa Kemal Bulvarı, No: 42, Daire: 8"),


        # ŞUBE PERSONELLERİ

        Kullanicilar(rol_id=sube_personeli.id, ad="Işıkhan", soyad="Işık", kullanici_adi="isikhanisik", email="isikhan@gmail.com", sifre=generate_password_hash("123456"), telefon="05341234569", adres="Isparta Merkez, Yayla Mahallesi, 1305 Sokak, No: 12, Daire: 4"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Efe", soyad="Sarıhan", kullanici_adi="efesarihan", email="efe@gmail.com", sifre=generate_password_hash("123456"), telefon="05351234570", adres="Antalya Muratpaşa, Fener Mahallesi, Tekelioğlu Caddesi, No: 35, Daire: 7"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Berrin", soyad="Ünsal", kullanici_adi="berrinunsal", email="berrin@gmail.com", sifre=generate_password_hash("123456"), telefon="05361234571", adres="Konya Selçuklu, Yazır Mahallesi, Şafak Caddesi, No: 24, Daire: 6"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Mehmet", soyad="Ertan", kullanici_adi="mehmetertan", email="mehmet@gmail.com", sifre=generate_password_hash("123456"), telefon="05371234572", adres="İstanbul Kadıköy, Feneryolu Mahallesi, Bağdat Caddesi, No: 156, Daire: 9"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Tuğba", soyad="Atcı", kullanici_adi="tugbaatci", email="tugba@gmail.com", sifre=generate_password_hash("123456"), telefon="05381234573", adres="İzmir Bornova, Kazımdirik Mahallesi, Üniversite Caddesi, No: 27, Daire: 3"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Zübeyde", soyad="Erten", kullanici_adi="zubeydeerten", email="zubeyde@gmail.com", sifre=generate_password_hash("123456"), telefon="05391234574", adres="Bursa Nilüfer, Görükle Mahallesi, Atatürk Bulvarı, No: 41, Daire: 10"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Murat Can", soyad="Gök", kullanici_adi="muratcangok", email="muratcan@gmail.com", sifre=generate_password_hash("123456"), telefon="05401234575", adres="Adana Seyhan, Reşatbey Mahallesi, Gazipaşa Bulvarı, No: 63, Daire: 5"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Ahmet", soyad="Gürdal", kullanici_adi="ahmetgurdal", email="ahmet@gmail.com", sifre=generate_password_hash("123456"), telefon="05411234576", adres="Eskişehir Tepebaşı, Hoşnudiye Mahallesi, İsmet İnönü Caddesi, No: 29, Daire: 8"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Şeyma", soyad="Özyiğit", kullanici_adi="seymaozyigit", email="seyma@gmail.com", sifre=generate_password_hash("123456"), telefon="05421234577", adres="Kayseri Melikgazi, Alpaslan Mahallesi, Kışla Caddesi, No: 17, Daire: 2"),

        Kullanicilar(rol_id=sube_personeli.id, ad="Derya", soyad="Aksoy", kullanici_adi="deryaaksoy", email="derya@gmail.com", sifre=generate_password_hash("123456"), telefon="05431234578", adres="Samsun Atakum, Cumhuriyet Mahallesi, İsmet İnönü Bulvarı, No: 52, Daire: 11"),


        # KURYELER

        Kullanicilar(rol_id=kurye.id, ad="Bengisu", soyad="Özilhan", kullanici_adi="bengisuozilhan", email="bengisu@gmail.com", sifre=generate_password_hash("123456"), telefon="05441234579", adres="Isparta Merkez, Bahçelievler Mahallesi, 3021 Sokak, No: 14, Daire: 6"),

        Kullanicilar(rol_id=kurye.id, ad="Cemile", soyad="Acar", kullanici_adi="cemileacar", email="cemile@gmail.com", sifre=generate_password_hash("123456"), telefon="05451234580", adres="Antalya Kepez, Yeni Emek Mahallesi, 2417 Sokak, No: 28, Daire: 4"),

        Kullanicilar(rol_id=kurye.id, ad="Merve", soyad="Oflaz", kullanici_adi="merveoflaz", email="merve@gmail.com", sifre=generate_password_hash("123456"), telefon="05461234581", adres="Konya Meram, Havzan Mahallesi, Alparslan Türkeş Caddesi, No: 36, Daire: 7"),

        Kullanicilar(rol_id=kurye.id, ad="Zehra", soyad="Güneş", kullanici_adi="zehragunes", email="zehra@gmail.com", sifre=generate_password_hash("123456"), telefon="05471234582", adres="İstanbul Üsküdar, Acıbadem Mahallesi, Acıbadem Caddesi, No: 74, Daire: 12"),

        Kullanicilar(rol_id=kurye.id, ad="Eda", soyad="Erdem", kullanici_adi="edaerdem", email="eda@gmail.com", sifre=generate_password_hash("123456"), telefon="05481234583", adres="İzmir Karşıyaka, Bostanlı Mahallesi, Cemal Gürsel Caddesi, No: 91, Daire: 5"),

        Kullanicilar(rol_id=kurye.id, ad="Bedirhan", soyad="Bülbül", kullanici_adi="bedirhanbulbul", email="bedirhan@gmail.com", sifre=generate_password_hash("123456"), telefon="05491234584", adres="Bursa Osmangazi, Çırpan Mahallesi, Darmstad Caddesi, No: 19, Daire: 3"),

        Kullanicilar(rol_id=kurye.id, ad="Süleyman", soyad="Demirel", kullanici_adi="suleymandemirel", email="suleyman@gmail.com", sifre=generate_password_hash("123456"), telefon="05501234585", adres="Ankara Keçiören, Etlik Mahallesi, General Dr. Tevfik Sağlam Caddesi, No: 45, Daire: 9"),

        Kullanicilar(rol_id=kurye.id, ad="Burcu", soyad="Özberk", kullanici_adi="burcuozberk", email="burcu@gmail.com", sifre=generate_password_hash("123456"), telefon="05511234586", adres="Adana Çukurova, Mahfesığmaz Mahallesi, Turgut Özal Bulvarı, No: 83, Daire: 6"),

        Kullanicilar(rol_id=kurye.id, ad="Emre", soyad="Kaya", kullanici_adi="emrekaya", email="emre@gmail.com", sifre=generate_password_hash("123456"), telefon="05521234587", adres="Eskişehir Odunpazarı, Vişnelik Mahallesi, Atatürk Bulvarı, No: 31, Daire: 4"),

        Kullanicilar(rol_id=kurye.id, ad="Selin", soyad="Yıldız", kullanici_adi="selinyildiz", email="selin@gmail.com", sifre=generate_password_hash("123456"), telefon="05531234588", adres="Kayseri Kocasinan, Erciyes Mahallesi, Kocasinan Bulvarı, No: 57, Daire: 8"),

        Kullanicilar(rol_id=kurye.id, ad="Onur", soyad="Çelik", kullanici_adi="onurcelik", email="onur@gmail.com", sifre=generate_password_hash("123456"), telefon="05541234589", adres="Samsun İlkadım, Kadıköy Mahallesi, Cumhuriyet Caddesi, No: 22, Daire: 5"),

        Kullanicilar(rol_id=kurye.id, ad="Damla", soyad="Kurt", kullanici_adi="damlakurt", email="damla@gmail.com", sifre=generate_password_hash("123456"), telefon="05551234590", adres="Isparta Merkez, Çünür Mahallesi, 102. Cadde, No: 16, Daire: 7"),

        Kullanicilar(rol_id=kurye.id, ad="Burak", soyad="Aydın", kullanici_adi="burakaydin", email="burakaydin@gmail.com", sifre=generate_password_hash("123456"), telefon="05561234591", adres="Antalya Konyaaltı, Gürsu Mahallesi, Atatürk Bulvarı, No: 48, Daire: 10"),

        Kullanicilar(rol_id=kurye.id, ad="Seda", soyad="Arslan", kullanici_adi="sedaarslan", email="seda@gmail.com", sifre=generate_password_hash("123456"), telefon="05571234592", adres="Konya Karatay, Akabe Mahallesi, Ankara Caddesi, No: 72, Daire: 3"),

        Kullanicilar(rol_id=kurye.id, ad="Tolga", soyad="Şahin", kullanici_adi="tolgasahin", email="tolga@gmail.com", sifre=generate_password_hash("123456"), telefon="05581234593", adres="İstanbul Pendik, Yenişehir Mahallesi, Millet Caddesi, No: 25, Daire: 6"),


        # MÜŞTERİLER

        Kullanicilar(rol_id=musteri.id, ad="Büşra", soyad="Develi", kullanici_adi="busradeveli", email="busra@gmail.com", sifre=generate_password_hash("123456"), telefon="05591234594", adres="Isparta Merkez, Modernevler Mahallesi, 3104 Sokak, No: 12, Daire: 5"),

        Kullanicilar(rol_id=musteri.id, ad="Mustafa", soyad="Yalçın", kullanici_adi="mustafayalcin", email="mustafa@gmail.com", sifre=generate_password_hash("123456"), telefon="05601234595", adres="Konya Selçuklu, Bosna Hersek Mahallesi, Yeni İstanbul Caddesi, No: 86, Daire: 9"),

        Kullanicilar(rol_id=musteri.id, ad="Şenay", soyad="Kaya", kullanici_adi="senaykaya", email="senay@gmail.com", sifre=generate_password_hash("123456"), telefon="05611234596", adres="Ankara Yenimahalle, Batıkent Mahallesi, İnönü Caddesi, No: 34, Daire: 7"),

        Kullanicilar(rol_id=musteri.id, ad="Arda", soyad="Keçeci", kullanici_adi="ardakececi", email="arda@gmail.com", sifre=generate_password_hash("123456"), telefon="05621234597", adres="İstanbul Beylikdüzü, Adnan Kahveci Mahallesi, Yavuz Sultan Selim Bulvarı, No: 58, Daire: 11"),

        Kullanicilar(rol_id=musteri.id, ad="Burak", soyad="Sezer", kullanici_adi="buraksezer", email="burak@gmail.com", sifre=generate_password_hash("123456"), telefon="05631234598", adres="İzmir Buca, Şirinyer Mahallesi, Menderes Caddesi, No: 47, Daire: 4"),

        Kullanicilar(rol_id=musteri.id, ad="Atilla", soyad="İlhan", kullanici_adi="atillailhan", email="atilla@gmail.com", sifre=generate_password_hash("123456"), telefon="05641234599", adres="Bursa Yıldırım, Mimarsinan Mahallesi, Ankara Yolu Caddesi, No: 63, Daire: 8"),

        Kullanicilar(rol_id=musteri.id, ad="Volkan", soyad="Demirel", kullanici_adi="volkandemirel", email="volkan@gmail.com", sifre=generate_password_hash("123456"), telefon="05651234600", adres="Adana Seyhan, Gürselpaşa Mahallesi, Aliya İzzetbegoviç Bulvarı, No: 29, Daire: 6"),

        Kullanicilar(rol_id=musteri.id, ad="Melih", soyad="Güler", kullanici_adi="melihguler", email="melih@gmail.com", sifre=generate_password_hash("123456"), telefon="05661234601", adres="Eskişehir Tepebaşı, Şirintepe Mahallesi, Sivrihisar Caddesi, No: 18, Daire: 3"),

        Kullanicilar(rol_id=musteri.id, ad="Ziya", soyad="Yazıcı", kullanici_adi="ziyayazici", email="ziya@gmail.com", sifre=generate_password_hash("123456"), telefon="05671234602", adres="Kayseri Melikgazi, Bahçelievler Mahallesi, Talas Bulvarı, No: 44, Daire: 10"),

        Kullanicilar(rol_id=musteri.id, ad="Miraç", soyad="Özer", kullanici_adi="miracozer", email="miracozer@gmail.com", sifre=generate_password_hash("123456"), telefon="05681234603", adres="Antalya Muratpaşa, Yeşilbahçe Mahallesi, Metin Kasapoğlu Caddesi, No: 71, Daire: 5"),

        Kullanicilar(rol_id=musteri.id, ad="Nazım", soyad="Hikmet", kullanici_adi="nazimhikmet", email="nazim@gmail.com", sifre=generate_password_hash("123456"), telefon="05691234604", adres="Samsun Atakum, Yenimahalle Mahallesi, Atatürk Bulvarı, No: 38, Daire: 7"),

        Kullanicilar(rol_id=musteri.id, ad="Ayşegül", soyad="Yılmaz", kullanici_adi="aysegulyilmaz", email="aysegul@gmail.com", sifre=generate_password_hash("123456"), telefon="05701234605", adres="Isparta Merkez, Pirimehmet Mahallesi, Cumhuriyet Caddesi, No: 21, Daire: 4"),

        Kullanicilar(rol_id=musteri.id, ad="Fikret", soyad="Tekin", kullanici_adi="fikrettekin", email="fikret@gmail.com", sifre=generate_password_hash("123456"), telefon="05711234606", adres="Konya Meram, Yenişehir Mahallesi, Gazze Caddesi, No: 55, Daire: 9"),

        Kullanicilar(rol_id=musteri.id, ad="Leyla", soyad="Ünsal", kullanici_adi="leylaunsal", email="leyla@gmail.com", sifre=generate_password_hash("123456"), telefon="05721234607", adres="Ankara Etimesgut, Eryaman Mahallesi, Göksu Caddesi, No: 32, Daire: 6"),

        Kullanicilar(rol_id=musteri.id, ad="Canan", soyad="Candan", kullanici_adi="canancandan", email="canan@gmail.com", sifre=generate_password_hash("123456"), telefon="05731234608", adres="İstanbul Maltepe, Küçükyalı Mahallesi, Bağdat Caddesi, No: 124, Daire: 8"),

        Kullanicilar(rol_id=musteri.id, ad="Bedir", soyad="Toprak", kullanici_adi="bedirtoprak", email="bedir@gmail.com", sifre=generate_password_hash("123456"), telefon="05741234609", adres="İzmir Karabağlar, Bahar Mahallesi, İnönü Caddesi, No: 67, Daire: 5"),

        Kullanicilar(rol_id=musteri.id, ad="Ece", soyad="Kara", kullanici_adi="ecekara", email="ece@gmail.com", sifre=generate_password_hash("123456"), telefon="05751234610", adres="Bursa Osmangazi, Demirtaş Mahallesi, Ankara Yolu Caddesi, No: 82, Daire: 12"),

        Kullanicilar(rol_id=musteri.id, ad="Mert", soyad="Öztürk", kullanici_adi="mertozturk", email="mert@gmail.com", sifre=generate_password_hash("123456"), telefon="05761234611", adres="Adana Çukurova, Yurt Mahallesi, Kenan Evren Bulvarı, No: 49, Daire: 3"),

        Kullanicilar(rol_id=musteri.id, ad="Deniz", soyad="Koç", kullanici_adi="denizkoc", email="deniz@gmail.com", sifre=generate_password_hash("123456"), telefon="05771234612", adres="Eskişehir Odunpazarı, Yenidoğan Mahallesi, Gazi Yakup Satar Caddesi, No: 26, Daire: 7"),

        Kullanicilar(rol_id=musteri.id, ad="Sinem", soyad="Acar", kullanici_adi="sinemacar", email="sinem@gmail.com", sifre=generate_password_hash("123456"), telefon="05781234613", adres="Isparta Merkez, Fatih Mahallesi, 2024 Sokak, No: 39, Daire: 5")
    ]

    db.session.add_all(kullanicilar)
    db.session.commit()

    print("47 kullanıcı başarıyla eklendi.")