from app import db
from datetime import datetime


class Rol(db.Model):
    __tablename__="roller"
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False, unique=True)
    kullanicilar = db.relationship("Kullanicilar", backref="rol", lazy=True)


class Kullanicilar(db.Model):
    __tablename__="kullanicilar"
    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey("roller.id"), nullable=False)
    sifre = db.Column(db.String(250), nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    kullanici_adi = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefon = db.Column(db.String(20), nullable=True)
    adres = db.Column(db.String(500), nullable=True)
    profil_fotografi = db.Column(db.String(255), nullable=True)
    kayit_tarihi = db.Column(db.DateTime, nullable=False, default=datetime.now)
    aktif = db.Column(db.Boolean, nullable=False, default=True)


class Subeler(db.Model):
    __tablename__="subeler"
    id = db.Column(db.Integer, primary_key=True)
    sube_ad = db.Column(db.String(50), nullable=False)
    il = db.Column(db.String(50), nullable=False)
    ilce = db.Column(db.String(50), nullable=False)
    adres = db.Column(db.String(500), nullable=False)
    telefon = db.Column(db.String(50), nullable=False)
    aktif = db.Column(db.Boolean, nullable=False, default=True)


class Kuryeler(db.Model):
    __tablename__="kuryeler"
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=False)
    telefon = db.Column(db.String(50), nullable=False)
    aktif = db.Column(db.Boolean, nullable=False, default=True)

    kullanici = db.relationship("Kullanicilar", backref="kurye", uselist=False)
    sube = db.relationship("Subeler", backref="kuryeler", lazy=True)


class SubePersonelleri(db.Model):
    __tablename__="sube_personelleri"
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=False)
    telefon = db.Column(db.String(50), nullable=False)
    gorev = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, nullable=False, default=True)

    kullanici = db.relationship("Kullanicilar", backref="sube_personeli", uselist=False)
    sube = db.relationship("Subeler", backref="personeller", lazy=True)


class KargoTurleri(db.Model):
    __tablename__="kargo_turleri"
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False, unique=True)
    aciklama = db.Column(db.String(250), nullable=True)
    ek_ucret = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    aktif = db.Column(db.Boolean, nullable=False, default=True)

    kargolar = db.relationship("Kargolar", backref="kargo_turu", lazy=True)


class Kargolar(db.Model):
    __tablename__="kargolar"
    id = db.Column(db.Integer, primary_key=True)
    takip_no = db.Column(db.String(50), nullable=False, unique=True)
    barkod = db.Column(db.String(100), nullable=True, unique=True)
    qr_kodu = db.Column(db.String(255), nullable=True)

    gonderici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=True)
    gonderici = db.Column(db.String(50), nullable=False)
    gonderici_telefon = db.Column(db.String(50), nullable=False)
    gonderici_adres = db.Column(db.String(500), nullable=False)

    alici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=True)
    alici = db.Column(db.String(50), nullable=False)
    alici_telefon = db.Column(db.String(50), nullable=False)
    alici_adres = db.Column(db.String(500), nullable=False)

    kargo_turu_id = db.Column(db.Integer, db.ForeignKey("kargo_turleri.id"), nullable=True)

    durum = db.Column(db.String(50), nullable=False)
    agirlik = db.Column(db.Numeric(10, 2), nullable=False)
    desi = db.Column(db.Numeric(10, 2), nullable=True)
    ucret = db.Column(db.Numeric(10, 2), nullable=False)

    gonderim_tarihi = db.Column(db.DateTime, nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, nullable=False, default=datetime.now)
    beklenen_teslim_tarihi = db.Column(db.DateTime, nullable=True)
    teslim_tarihi = db.Column(db.DateTime, nullable=True)
    gecikme_durumu = db.Column(db.Boolean, nullable=False, default=False)

    cikis_sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=True)
    varis_sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=True)
    sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=False)
    kurye_id = db.Column(db.Integer, db.ForeignKey("kuryeler.id"), nullable=True)

    gonderici_kullanici = db.relationship("Kullanicilar", foreign_keys=[gonderici_id], backref="gonderdigi_kargolar")
    alici_kullanici = db.relationship("Kullanicilar", foreign_keys=[alici_id], backref="aldigi_kargolar")

    kurye = db.relationship("Kuryeler", backref="kargolar", lazy=True)
    sube = db.relationship("Subeler", foreign_keys=[sube_id], backref="kargolar", lazy=True)
    cikis_sube = db.relationship("Subeler", foreign_keys=[cikis_sube_id], backref="cikis_kargolari", lazy=True)
    varis_sube = db.relationship("Subeler", foreign_keys=[varis_sube_id], backref="varis_kargolari", lazy=True)

    hareketler = db.relationship("Kargo_Hareketleri", backref="kargo", lazy=True)
    bildirimler = db.relationship("Bildirimler", backref="kargo", lazy=True)
    degerlendirmeler = db.relationship("Degerlendirmeler", backref="kargo", lazy=True)


class Kargo_Hareketleri(db.Model):
    __tablename__="kargo_hareketleri"
    id = db.Column(db.Integer, primary_key=True)
    kargo_id = db.Column(db.Integer, db.ForeignKey("kargolar.id"), nullable=False)
    sube_id = db.Column(db.Integer, db.ForeignKey("subeler.id"), nullable=True)
    kurye_id = db.Column(db.Integer, db.ForeignKey("kuryeler.id"), nullable=True)
    durum = db.Column(db.String(50), nullable=False)
    aciklama = db.Column(db.String(250), nullable=False)
    konum = db.Column(db.String(250), nullable=True)
    tarih = db.Column(db.DateTime, nullable=False, default=datetime.now)

    sube = db.relationship("Subeler", backref="kargo_hareketleri", lazy=True)
    kurye = db.relationship("Kuryeler", backref="kargo_hareketleri", lazy=True)


class Bildirimler(db.Model):
    __tablename__="bildirimler"
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    kargo_id = db.Column(db.Integer, db.ForeignKey("kargolar.id"), nullable=True)
    baslik = db.Column(db.String(150), nullable=False)
    mesaj = db.Column(db.String(500), nullable=False)
    okundu = db.Column(db.Boolean, nullable=False, default=False)
    tarih = db.Column(db.DateTime, nullable=False, default=datetime.now)

    kullanici = db.relationship("Kullanicilar", backref="bildirimler", lazy=True)


class AktiviteLoglari(db.Model):
    __tablename__="aktivite_loglari"
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=True)
    kargo_id = db.Column(db.Integer, db.ForeignKey("kargolar.id"), nullable=True)
    islem = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.String(500), nullable=False)
    tarih = db.Column(db.DateTime, nullable=False, default=datetime.now)

    kullanici = db.relationship("Kullanicilar", backref="aktivite_loglari", lazy=True)
    kargo = db.relationship("Kargolar", backref="aktivite_loglari", lazy=True)


class KargoDurumGecisleri(db.Model):
    __tablename__="kargo_durum_gecisleri"
    id = db.Column(db.Integer, primary_key=True)
    mevcut_durum = db.Column(db.String(50), nullable=False)
    sonraki_durum = db.Column(db.String(50), nullable=False)
    aktif = db.Column(db.Boolean, nullable=False, default=True)


class Degerlendirmeler(db.Model):
    __tablename__="degerlendirmeler"
    id = db.Column(db.Integer, primary_key=True)
    kargo_id = db.Column(db.Integer, db.ForeignKey("kargolar.id"), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)
    puan = db.Column(db.Integer, nullable=False)
    yorum = db.Column(db.String(500), nullable=True)
    tarih = db.Column(db.DateTime, nullable=False, default=datetime.now)

    kullanici = db.relationship("Kullanicilar", backref="degerlendirmeler", lazy=True)