from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import (Rol,Kullanicilar,Kargolar,Kargo_Hareketleri,Subeler,Kuryeler,SubePersonelleri,Bildirimler,Degerlendirmeler,KargoTurleri)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import random

main = Blueprint("main", __name__)

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================
def bildirim_olustur(kullanici_id, baslik, mesaj, kargo_id=None):

    bildirim = Bildirimler(
        kullanici_id=kullanici_id,
        kargo_id=kargo_id,
        baslik=baslik,
        mesaj=mesaj,
        okundu=False,
        tarih=datetime.now()
    )

    db.session.add(bildirim)

@main.route("/fiyat-hesapla")
def fiyat_hesapla():

    kargo_turleri = KargoTurleri.query.all()

    return render_template(
        "fiyat_hesapla.html",
        kargo_turleri=kargo_turleri
    )
def turkce_normalize(metin):

    if not metin:
        return ""

    ceviri = str.maketrans({
        "Ç": "c",
        "ç": "c",
        "Ğ": "g",
        "ğ": "g",
        "İ": "i",
        "I": "i",
        "ı": "i",
        "Ö": "o",
        "ö": "o",
        "Ş": "s",
        "ş": "s",
        "Ü": "u",
        "ü": "u"
    })

    return metin.translate(ceviri).lower().strip()


# =========================================================
# KARGO OLUŞTURMA YARDIMCI FONKSİYONLARI
# =========================================================

def adres_sube_uyumlu_mu(adres, sube):
    """Adres metninde şubenin ili geçiyorsa True döndürür."""

    if not adres or not sube or not sube.il:
        return False

    normalize_adres = turkce_normalize(adres)
    normalize_il = turkce_normalize(sube.il)

    # Noktalama işaretlerini boşluğa çevirerek il adını kelime olarak ara.
    temiz_adres = "".join(
        karakter if karakter.isalnum() else " "
        for karakter in normalize_adres
    )

    return normalize_il in temiz_adres.split()


def adrese_gore_aktif_subeleri_getir(adres):
    """Yalnızca adresteki şehirle eşleşen aktif şubeleri getirir."""

    aktif_subeler = (
        Subeler.query
        .filter_by(aktif=True)
        .order_by(Subeler.sube_ad)
        .all()
    )

    return [
        sube
        for sube in aktif_subeler
        if adres_sube_uyumlu_mu(adres, sube)
    ]


def kargo_ucreti_hesapla(agirlik, desi, kargo_turu):
    """Temel ücrete kargo türünün ek ücretini ekleyerek toplamı döndürür."""

    ucretlendirme_degeri = max(agirlik, desi)

    if ucretlendirme_degeri <= 1:
        temel_ucret = 50
    elif ucretlendirme_degeri <= 3:
        temel_ucret = 75
    elif ucretlendirme_degeri <= 5:
        temel_ucret = 100
    else:
        temel_ucret = 100 + ((ucretlendirme_degeri - 5) * 20)

    ek_ucret = float(kargo_turu.ek_ucret or 0)
    toplam_ucret = temel_ucret + ek_ucret

    return (
        round(ucretlendirme_degeri, 2),
        round(temel_ucret, 2),
        round(ek_ucret, 2),
        round(toplam_ucret, 2)
    )

def giris_kontrolu():
    """Kullanıcının giriş yapıp yapmadığını kontrol eder."""
    return "kullanici_id" in session


def rol_kontrolu(rol):
    """Oturumdaki kullanıcının rolünü kontrol eder."""
    return session.get("rol") == rol


def mevcut_kullanici():
    """Oturumdaki kullanıcıyı getirir."""

    if "kullanici_id" not in session:
        return None

    return Kullanicilar.query.get(
        session["kullanici_id"]
    )


def musteri_kargolarini_getir():

    kullanici = mevcut_kullanici()

    if not kullanici:
        return []

    ad_soyad = (
        f"{kullanici.ad} {kullanici.soyad}"
    )

    return Kargolar.query.filter(
        db.or_(
            Kargolar.gonderici == ad_soyad,
            Kargolar.alici == ad_soyad
        )
    ).order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

def sube_personelini_getir():
    """Giriş yapan şube personelini getirir."""

    if "kullanici_id" not in session:
        return None

    return SubePersonelleri.query.filter_by(
        kullanici_id=session["kullanici_id"]
    ).first()


def kuryeyi_getir():
    """Giriş yapan kuryeyi getirir."""

    if "kullanici_id" not in session:
        return None

    return Kuryeler.query.filter_by(
        kullanici_id=session["kullanici_id"]
    ).first()


def kargo_hareketlerini_getir(kargo_id):
    """Kargonun hareketlerini tarih sırasına göre getirir."""

    return Kargo_Hareketleri.query.filter_by(
        kargo_id=kargo_id
    ).order_by(
        Kargo_Hareketleri.tarih.asc()
    ).all()


# =========================================================
# ANA SAYFA
# =========================================================

@main.route("/")
def index():
    return render_template("index.html")


# =========================================================
# MÜŞTERİ GİRİŞİ
# =========================================================

@main.route("/musteri_login", methods=["GET", "POST"])
def musteri_login():

    # Login ekranına gelindiğinde mevcut kullanıcı oturumunu temizle
    session.pop("kullanici_id", None)
    session.pop("rol", None)
    session.pop("kullanici_adi", None)
    session.pop("personel_id", None)
    session.pop("kurye_id", None)
    session.pop("sube_id", None)

    if request.method == "POST":

        email = request.form.get("email")
        sifre = request.form.get("sifre")

        kullanici = Kullanicilar.query.filter_by(
            email=email
        ).first()

        if not kullanici or not check_password_hash(
            kullanici.sifre,
            sifre
        ):
            flash("E-posta veya şifre hatalı.")
            return render_template(
                "login/musteri_login.html"
            )

        if kullanici.rol.ad != "Müşteri":
            flash("Bu hesap müşteri hesabı değil.")
            return render_template(
                "login/musteri_login.html"
            )

        session["kullanici_id"] = kullanici.id
        session["rol"] = kullanici.rol.ad
        session["kullanici_adi"] = kullanici.kullanici_adi

        return redirect(
            url_for("main.musteri_panel")
        )

    return render_template(
        "login/musteri_login.html"
    )
# =========================================================
# MÜŞTERİ KAYIT
# =========================================================

@main.route(
    "/musteri_kayit",
    methods=["GET", "POST"]
)
def musteri_kayit():

    if request.method == "POST":

        ad = request.form.get(
            "ad",
            ""
        ).strip()

        soyad = request.form.get(
            "soyad",
            ""
        ).strip()

        kullanici_adi = request.form.get(
            "kullanici_adi",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        sifre = request.form.get(
            "sifre",
            ""
        )

        sifre_tekrar = request.form.get(
            "sifre_tekrar",
            ""
        )

        telefon = request.form.get(
            "telefon",
            ""
        ).strip()

        adres = request.form.get(
            "adres",
            ""
        ).strip()

        # =================================================
        # ZORUNLU ALAN KONTROLÜ
        # =================================================

        if not all([
            ad,
            soyad,
            kullanici_adi,
            email,
            sifre,
            sifre_tekrar
        ]):

            flash(
                "Lütfen zorunlu alanları doldurunuz.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        # =================================================
        # ŞİFRE KONTROLÜ
        # =================================================

        if sifre != sifre_tekrar:

            flash(
                "Şifreler birbiriyle eşleşmiyor.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        if len(sifre) < 6:

            flash(
                "Şifre en az 6 karakter olmalıdır.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        # =================================================
        # KULLANICI ADI KONTROLÜ
        # =================================================

        mevcut_kullanici = Kullanicilar.query.filter_by(
            kullanici_adi=kullanici_adi
        ).first()

        if mevcut_kullanici:

            flash(
                "Bu kullanıcı adı zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        # =================================================
        # E-POSTA KONTROLÜ
        # =================================================

        mevcut_email = Kullanicilar.query.filter_by(
            email=email
        ).first()

        if mevcut_email:

            flash(
                "Bu e-posta adresi zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        # =================================================
        # MÜŞTERİ ROLÜ
        # =================================================

        musteri_rolu = Rol.query.filter_by(
            ad="Müşteri"
        ).first()

        if not musteri_rolu:

            flash(
                "Müşteri rolü bulunamadı.",
                "danger"
            )

            return render_template(
                "login/musteri_kayit.html"
            )

        # =================================================
        # KULLANICI OLUŞTUR
        # =================================================

        yeni_kullanici = Kullanicilar(

            rol_id=musteri_rolu.id,

            sifre=generate_password_hash(
                sifre
            ),

            ad=ad,

            soyad=soyad,

            kullanici_adi=kullanici_adi,

            email=email,

            telefon=telefon or None,

            adres=adres or None

        )

        db.session.add(
            yeni_kullanici
        )

        db.session.commit()

        flash(
            "Hesabınız başarıyla oluşturuldu. "
            "Giriş yapabilirsiniz.",
            "success"
        )

        return redirect(
            url_for(
                "main.musteri_login"
            )
        )

    return render_template(
        "login/musteri_kayit.html"
    )

# =========================================================
# MÜŞTERİ PANELİ
# =========================================================

@main.route("/musteri_panel")
def musteri_panel():

    if not giris_kontrolu():
        return redirect(
            url_for("main.musteri_login")
        )

    if not rol_kontrolu("Müşteri"):
        return redirect(
            url_for("main.index")
        )

    return render_template(
        "panel/musteri_panel.html"
    )
# =========================================================
# MÜŞTERİ - KARGOLARIM
# =========================================================

@main.route("/musteri/kargolarim")
def kargolarim():

    # -----------------------------------------------------
    # GİRİŞ KONTROLÜ
    # -----------------------------------------------------

    if not giris_kontrolu():

        return redirect(
            url_for("main.musteri_login")
        )

    # -----------------------------------------------------
    # ROL KONTROLÜ
    # -----------------------------------------------------

    if not rol_kontrolu("Müşteri"):

        return redirect(
            url_for("main.index")
        )

    # -----------------------------------------------------
    # KULLANICI
    # -----------------------------------------------------

    kullanici = mevcut_kullanici()

    if not kullanici:

        flash(
            "Kullanıcı bilgileri bulunamadı.",
            "danger"
        )

        return redirect(
            url_for("main.musteri_login")
        )

    # -----------------------------------------------------
    # KULLANICININ KARGOLARI
    # -----------------------------------------------------

    kargolar = musteri_kargolarini_getir()

    # -----------------------------------------------------
    # KULLANICININ DAHA ÖNCE DEĞERLENDİRDİĞİ KARGOLAR
    # -----------------------------------------------------

    degerlendirmeler = Degerlendirmeler.query.filter_by(
        kullanici_id=kullanici.id
    ).all()

    degerlendirilmis_kargolar = {
        degerlendirme.kargo_id
        for degerlendirme in degerlendirmeler
    }

    # -----------------------------------------------------
    # SAYFAYI GÖSTER
    # -----------------------------------------------------

    return render_template(
        "musteri/kargolarim.html",
        kargolar=kargolar,
        kullanici=kullanici,
        degerlendirilmis_kargolar=degerlendirilmis_kargolar
    )
# =========================================================
# MÜŞTERİ - KARGO DEĞERLENDİR
# =========================================================

@main.route(
    "/musteri/kargo/<int:kargo_id>/degerlendir",
    methods=["GET", "POST"]
)
def kargo_degerlendir(kargo_id):

    # -----------------------------------------------------
    # GİRİŞ KONTROLÜ
    # -----------------------------------------------------

    if not giris_kontrolu():

        return redirect(
            url_for("main.musteri_login")
        )

    # -----------------------------------------------------
    # ROL KONTROLÜ
    # -----------------------------------------------------

    if not rol_kontrolu("Müşteri"):

        return redirect(
            url_for("main.index")
        )

    # -----------------------------------------------------
    # KULLANICI
    # -----------------------------------------------------

    kullanici = mevcut_kullanici()

    if not kullanici:

        flash(
            "Kullanıcı bilgileri bulunamadı.",
            "danger"
        )

        return redirect(
            url_for("main.musteri_login")
        )

    # -----------------------------------------------------
    # KARGOYU BUL
    # -----------------------------------------------------

    kargo = Kargolar.query.filter_by(
        id=kargo_id
    ).first()

    if not kargo:

        flash(
            "Kargo bulunamadı.",
            "danger"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # -----------------------------------------------------
    # KARGO BU KULLANICIYA AİT Mİ?
    # -----------------------------------------------------

    ad_soyad = f"{kullanici.ad} {kullanici.soyad}"

    if (
        kargo.gonderici != ad_soyad
        and kargo.alici != ad_soyad
    ):

        flash(
            "Bu kargoyu değerlendirme yetkiniz bulunmuyor.",
            "danger"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # -----------------------------------------------------
    # SADECE TESLİM EDİLEN KARGOLAR
    # -----------------------------------------------------

    if kargo.durum != "Teslim Edildi":

        flash(
            "Sadece teslim edilmiş kargolar değerlendirilebilir.",
            "warning"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # -----------------------------------------------------
    # DAHA ÖNCE DEĞERLENDİRİLMİŞ Mİ?
    # -----------------------------------------------------

    mevcut_degerlendirme = Degerlendirmeler.query.filter_by(
        kargo_id=kargo.id,
        kullanici_id=kullanici.id
    ).first()

    if mevcut_degerlendirme:

        flash(
            "Bu kargoyu daha önce değerlendirdiniz.",
            "info"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # -----------------------------------------------------
    # POST - DEĞERLENDİRME KAYDET
    # -----------------------------------------------------

    if request.method == "POST":

        puan = request.form.get(
            "puan",
            type=int
        )

        yorum = request.form.get(
            "yorum",
            ""
        ).strip()

        # -------------------------------------------------
        # PUAN KONTROLÜ
        # -------------------------------------------------

        if puan is None or puan < 1 or puan > 5:

            flash(
                "Lütfen 1 ile 5 arasında bir puan veriniz.",
                "danger"
            )

            return render_template(
                "musteri/kargo_degerlendir.html",
                kargo=kargo
            )

        # -------------------------------------------------
        # DEĞERLENDİRME OLUŞTUR
        # -------------------------------------------------

        degerlendirme = Degerlendirmeler(

            kargo_id=kargo.id,

            kullanici_id=kullanici.id,

            puan=puan,

            yorum=yorum if yorum else None,

            tarih=datetime.now()
        )

        # -------------------------------------------------
        # VERİTABANINA KAYDET
        # -------------------------------------------------

        db.session.add(
            degerlendirme
        )

        db.session.commit()

        flash(
            "Değerlendirmeniz başarıyla kaydedildi.",
            "success"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # -----------------------------------------------------
    # GET - DEĞERLENDİRME SAYFASINI AÇ
    # -----------------------------------------------------

    return render_template(
        "musteri/kargo_degerlendir.html",
        kargo=kargo
    )
# =========================================================
# MÜŞTERİ - KARGO OLUŞTUR
# =========================================================

@main.route(
    "/musteri/kargo/olustur",
    methods=["GET", "POST"]
)
def musteri_kargo_olustur():

    if not giris_kontrolu():
        return redirect(url_for("main.musteri_login"))

    if not rol_kontrolu("Müşteri"):
        return redirect(url_for("main.index"))

    kullanici = mevcut_kullanici()

    if not kullanici:
        flash("Kullanıcı bilgileri bulunamadı.", "danger")
        return redirect(url_for("main.musteri_login"))

    if not kullanici.adres:
        flash(
            "Profilinizde adres bilgisi bulunmuyor. "
            "Kargo oluşturmak için önce adresinizi güncelleyiniz.",
            "warning"
        )
        return redirect(url_for("main.profilim"))

    musteriler = (
        Kullanicilar.query
        .join(Rol, Kullanicilar.rol_id == Rol.id)
        .filter(Rol.ad == "Müşteri")
        .order_by(Kullanicilar.ad, Kullanicilar.soyad)
        .all()
    )

    # Yalnızca giriş yapan müşterinin adresindeki şehirdeki aktif şubeler.
    subeler = adrese_gore_aktif_subeleri_getir(kullanici.adres)

    kargo_turleri = (
        KargoTurleri.query
        .filter_by(aktif=True)
        .order_by(KargoTurleri.id)
        .all()
    )

    def formu_goster():
        return render_template(
            "musteri/kargo_olustur.html",
            kullanici=kullanici,
            musteriler=musteriler,
            subeler=subeler,
            kargo_turleri=kargo_turleri
        )

    if request.method == "GET" and not subeler:
        flash(
            "Profil adresinizin bulunduğu şehirde aktif şube bulunamadı "
            "veya adresinizden şehir tespit edilemedi.",
            "warning"
        )

    if request.method == "POST":

        alici_id = request.form.get("alici_id", type=int)
        sube_id = request.form.get("sube_id", type=int)
        kargo_turu_id = request.form.get("kargo_turu_id", type=int)

        agirlik = request.form.get("agirlik", "").strip()
        desi_en = request.form.get("desi_en", "").strip()
        desi_boy = request.form.get("desi_boy", "").strip()
        desi_yukseklik = request.form.get("desi_yukseklik", "").strip()

        if not alici_id:
            flash("Lütfen bir alıcı seçiniz.", "danger")
            return formu_goster()

        alici_kullanici = (
            Kullanicilar.query
            .join(Rol, Kullanicilar.rol_id == Rol.id)
            .filter(
                Kullanicilar.id == alici_id,
                Rol.ad == "Müşteri"
            )
            .first()
        )

        if not alici_kullanici:
            flash("Seçilen alıcı bulunamadı.", "danger")
            return formu_goster()

        if alici_kullanici.id == kullanici.id:
            flash("Kendinize kargo gönderemezsiniz.", "danger")
            return formu_goster()

        if not sube_id:
            flash("Lütfen bir gönderim şubesi seçiniz.", "danger")
            return formu_goster()

        # Formdan elle farklı bir şube ID'si gönderilmesini de engeller.
        sube = next(
            (sube for sube in subeler if sube.id == sube_id),
            None
        )

        if not sube:
            flash(
                "Yalnızca profil adresinizin bulunduğu şehirdeki "
                "aktif bir şubeyi seçebilirsiniz.",
                "danger"
            )
            return formu_goster()

        if not kargo_turu_id:
            flash("Lütfen bir kargo türü seçiniz.", "danger")
            return formu_goster()

        kargo_turu = KargoTurleri.query.filter_by(
            id=kargo_turu_id,
            aktif=True
        ).first()

        if not kargo_turu:
            flash("Seçilen kargo türü bulunamadı.", "danger")
            return formu_goster()

        try:
            agirlik = float(agirlik)
            if agirlik <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Ağırlık bilgisini doğru giriniz.", "danger")
            return formu_goster()

        try:
            desi_en = float(desi_en)
            desi_boy = float(desi_boy)
            desi_yukseklik = float(desi_yukseklik)

            if desi_en <= 0 or desi_boy <= 0 or desi_yukseklik <= 0:
                raise ValueError

        except (ValueError, TypeError):
            flash(
                "En, boy ve yükseklik bilgilerini doğru giriniz.",
                "danger"
            )
            return formu_goster()

        desi = (desi_en * desi_boy * desi_yukseklik) / 3000

        _, _, _, ucret = kargo_ucreti_hesapla(
            agirlik,
            desi,
            kargo_turu
        )

        gonderici = f"{kullanici.ad} {kullanici.soyad}"
        gonderici_telefon = kullanici.telefon or ""
        gonderici_adres = kullanici.adres or ""

        if not gonderici_telefon:
            flash(
                "Profilinizde telefon numarası bulunmuyor. "
                "Lütfen profil bilgilerinizi güncelleyiniz.",
                "danger"
            )
            return redirect(url_for("main.profilim"))

        alici = f"{alici_kullanici.ad} {alici_kullanici.soyad}"
        alici_telefon = alici_kullanici.telefon or ""
        alici_adres = alici_kullanici.adres or ""

        if not alici_telefon:
            flash("Seçilen müşterinin telefon bilgisi bulunmuyor.", "danger")
            return formu_goster()

        if not alici_adres:
            flash("Seçilen müşterinin adres bilgisi bulunmuyor.", "danger")
            return formu_goster()

        while True:
            takip_no = f"KRG{random.randint(100000, 999999)}"
            if not Kargolar.query.filter_by(takip_no=takip_no).first():
                break

        kargo = Kargolar(
            takip_no=takip_no,
            gonderici_id=kullanici.id,
            gonderici=gonderici,
            gonderici_telefon=gonderici_telefon,
            gonderici_adres=gonderici_adres,
            alici_id=alici_kullanici.id,
            alici=alici,
            alici_telefon=alici_telefon,
            alici_adres=alici_adres,
            kargo_turu_id=kargo_turu.id,
            durum="Hazırlanıyor",
            agirlik=agirlik,
            desi=round(desi, 2),
            ucret=ucret,
            gonderim_tarihi=datetime.now(),
            teslim_tarihi=None,
            sube_id=sube.id,
            kurye_id=None
        )

        try:
            db.session.add(kargo)
            db.session.flush()

            hareket = Kargo_Hareketleri(
                kargo_id=kargo.id,
                sube_id=sube.id,
                kurye_id=None,
                durum="Hazırlanıyor",
                aciklama=(
                    f"Kargo {sube.sube_ad} şubesinde "
                    f"{kargo_turu.ad} gönderi olarak oluşturuldu."
                ),
                tarih=datetime.now()
            )

            db.session.add(hareket)
            db.session.commit()

        except Exception:
            db.session.rollback()
            flash("Kargo oluşturulurken bir hata oluştu.", "danger")
            return formu_goster()

        flash(
            f"Kargo başarıyla oluşturuldu. "
            f"Takip numaranız: {takip_no} | "
            f"Toplam ücret: {ucret:.2f} ₺",
            "success"
        )

        return redirect(url_for("main.kargolarim"))

    return formu_goster()

@main.route("/musteri/kargo/<int:kargo_id>")
def musteri_kargo_detay(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.musteri_login")
        )

    if not rol_kontrolu("Müşteri"):
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    if not kullanici:

        flash(
            "Kullanıcı bilgileri bulunamadı.",
            "danger"
        )

        return redirect(
            url_for("main.musteri_login")
        )

    # =====================================================
    # KARGOYU BUL
    # =====================================================

    kargo = Kargolar.query.filter(
        db.or_(
            Kargolar.gonderici == (
                kullanici.ad + " " + kullanici.soyad
            ),
            Kargolar.alici == (
                kullanici.ad + " " + kullanici.soyad
            )
        ),
        Kargolar.id == kargo_id
    ).first()

    if not kargo:

        flash(
            "Bu kargo bulunamadı veya size ait değil.",
            "danger"
        )

        return redirect(
            url_for("main.kargolarim")
        )

    # =====================================================
    # KARGO HAREKETLERİ
    # =====================================================

    hareketler = Kargo_Hareketleri.query.filter_by(
        kargo_id=kargo.id
    ).order_by(
        Kargo_Hareketleri.tarih.asc()
    ).all()

    return render_template(
        "musteri/kargo_detay.html",

        kargo=kargo,

        hareketler=hareketler,

        kullanici=kullanici
    )
# =========================================================
# GENEL KARGO TAKİP
# =========================================================

@main.route("/takip", methods=["GET", "POST"])
def genel_kargo_takip():

    kargo = None
    takip_no = ""
    kargo_hareketleri = []

    if request.method == "POST":

        takip_no = request.form.get(
            "takip_no",
            ""
        ).strip()

        if not takip_no:

            flash(
                "Lütfen takip numarası giriniz."
            )

        else:

            kargo = Kargolar.query.filter_by(
                takip_no=takip_no
            ).first()

            if not kargo:

                flash(
                    "Bu takip numarasına ait kargo bulunamadı."
                )

            else:

                kargo_hareketleri = (
                    kargo_hareketlerini_getir(kargo.id)
                )

    return render_template(
        "musteri/kargo_takip_sonuc.html",
        kargo=kargo,
        takip_no=takip_no,
        kargo_hareketleri=kargo_hareketleri
    )


# =========================================================
# YÖNETİCİ GİRİŞİ
# =========================================================

@main.route("/yonetici_login", methods=["GET", "POST"])
def yonetici_login():

    # Login ekranına gelindiğinde mevcut kullanıcı oturumunu temizle
    session.pop("kullanici_id", None)
    session.pop("rol", None)
    session.pop("kullanici_adi", None)
    session.pop("personel_id", None)
    session.pop("kurye_id", None)
    session.pop("sube_id", None)

    if request.method == "POST":

        email = request.form.get("email")
        sifre = request.form.get("sifre")

        kullanici = Kullanicilar.query.filter_by(
            email=email
        ).first()

        if not kullanici or not check_password_hash(
            kullanici.sifre,
            sifre
        ):
            flash("E-posta veya şifre hatalı.")
            return render_template(
                "login/yonetici_login.html"
            )

        if kullanici.rol.ad != "Yönetici":
            flash("Bu hesap yönetici hesabı değil.")
            return render_template(
                "login/yonetici_login.html"
            )

        session["kullanici_id"] = kullanici.id
        session["rol"] = kullanici.rol.ad
        session["kullanici_adi"] = kullanici.kullanici_adi

        return redirect(
            url_for("main.yonetici_panel")
        )

    return render_template(
        "login/yonetici_login.html"
    )
# =========================================================
# YÖNETİCİ PANELİ
# =========================================================

@main.route("/yonetici_panel")
def yonetici_panel():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    yonetici = mevcut_kullanici()

    # =====================================================
    # TEMEL İSTATİSTİKLER
    # =====================================================

    toplam_kullanici = Kullanicilar.query.count()

    toplam_sube = Subeler.query.count()

    toplam_kurye = Kuryeler.query.count()

    toplam_kargo = Kargolar.query.count()

    # =====================================================
    # KURYE PERFORMANSLARI
    # =====================================================

    performanslar = kurye_performanslarini_getir()

    # =====================================================
    # KARGO DURUMLARI
    # =====================================================

    durum_sayilari = (
        db.session.query(
            Kargolar.durum,
            db.func.count(Kargolar.id)
        )
        .group_by(
            Kargolar.durum
        )
        .all()
    )

    kargo_durumlari = [
        durum
        for durum, sayi in durum_sayilari
    ]

    kargo_durum_sayilari = [
        sayi
        for durum, sayi in durum_sayilari
    ]

    # =====================================================
    # AYLIK KARGO SAYISI
    # =====================================================

    aylar = [
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık"
    ]

    aylik_sayilar = []

    mevcut_yil = datetime.now().year

    for ay in range(1, 13):

        sayi = (
            Kargolar.query
            .filter(
                db.extract(
                    "year",
                    Kargolar.gonderim_tarihi
                ) == mevcut_yil,
                db.extract(
                    "month",
                    Kargolar.gonderim_tarihi
                ) == ay
            )
            .count()
        )

        aylik_sayilar.append(
            sayi
        )

    # =====================================================
    # ŞUBELERE GÖRE KARGO SAYISI
    # =====================================================

    sube_sayilari = (
        db.session.query(
            Subeler.sube_ad,
            db.func.count(Kargolar.id)
        )
        .outerjoin(
            Kargolar,
            Kargolar.sube_id == Subeler.id
        )
        .group_by(
            Subeler.id,
            Subeler.sube_ad
        )
        .all()
    )

    sube_adlari = [
        sube_ad
        for sube_ad, sayi in sube_sayilari
    ]

    sube_kargo_sayilari = [
        sayi
        for sube_ad, sayi in sube_sayilari
    ]

    # =====================================================
    # KURYELERE GÖRE KARGO SAYISI
    # =====================================================

    kurye_sayilari = (
        db.session.query(
            Kullanicilar.ad,
            Kullanicilar.soyad,
            db.func.count(Kargolar.id)
        )
        .join(
            Kuryeler,
            Kuryeler.kullanici_id == Kullanicilar.id
        )
        .outerjoin(
            Kargolar,
            Kargolar.kurye_id == Kuryeler.id
        )
        .group_by(
            Kullanicilar.id,
            Kullanicilar.ad,
            Kullanicilar.soyad
        )
        .all()
    )

    kurye_adlari = [
        f"{ad} {soyad}"
        for ad, soyad, sayi in kurye_sayilari
    ]

    kurye_kargo_sayilari = [
        sayi
        for ad, soyad, sayi in kurye_sayilari
    ]

    # =====================================================
    # YÖNETİCİ PANELİNİ GÖNDER
    # =====================================================

    return render_template(
        "panel/yonetici_panel.html",

        yonetici=yonetici,

        # -------------------------
        # İSTATİSTİK KARTLARI
        # -------------------------

        toplam_kullanici=toplam_kullanici,
        toplam_sube=toplam_sube,
        toplam_kurye=toplam_kurye,
        toplam_kargo=toplam_kargo,

        # -------------------------
        # KURYE PERFORMANSI
        # -------------------------

        performanslar=performanslar,

        # -------------------------
        # KARGO DURUMLARI GRAFİĞİ
        # -------------------------

        kargo_durumlari=kargo_durumlari,
        kargo_durum_sayilari=kargo_durum_sayilari,

        # -------------------------
        # AYLIK KARGO GRAFİĞİ
        # -------------------------

        aylar=aylar,
        aylik_sayilar=aylik_sayilar,

        # -------------------------
        # ŞUBE GRAFİĞİ
        # -------------------------

        sube_adlari=sube_adlari,
        sube_kargo_sayilari=sube_kargo_sayilari,

        # -------------------------
        # KURYE GRAFİĞİ
        # -------------------------

        kurye_adlari=kurye_adlari,
        kurye_kargo_sayilari=kurye_kargo_sayilari
    )
# =========================================================
# YÖNETİCİ - KULLANICILAR
# =========================================================

@main.route("/yonetici/kullanicilar")
def yonetici_kullanicilar():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    # =====================================================
    # FİLTRELER
    # =====================================================

    kullanici_adi = request.args.get(
        "kullanici_adi",
        ""
    ).strip()

    ad_soyad = request.args.get(
        "ad_soyad",
        ""
    ).strip()

    email = request.args.get(
        "email",
        ""
    ).strip()

    rol_id = request.args.get(
        "rol_id",
        ""
    ).strip()

    # =====================================================
    # KULLANICILAR SORGUSU
    # =====================================================

    sorgu = Kullanicilar.query

    # =====================================================
    # KULLANICI ADI
    # =====================================================

    if kullanici_adi:

        sorgu = sorgu.filter(
            Kullanicilar.kullanici_adi.ilike(
                f"%{kullanici_adi}%"
            )
        )

    # =====================================================
    # AD SOYAD
    # =====================================================

    if ad_soyad:

        sorgu = sorgu.filter(
            db.or_(
                Kullanicilar.ad.ilike(
                    f"%{ad_soyad}%"
                ),
                Kullanicilar.soyad.ilike(
                    f"%{ad_soyad}%"
                )
            )
        )

    # =====================================================
    # E-POSTA
    # =====================================================

    if email:

        sorgu = sorgu.filter(
            Kullanicilar.email.ilike(
                f"%{email}%"
            )
        )

    # =====================================================
    # ROL
    # =====================================================

    if rol_id:

        try:

            rol_id_int = int(rol_id)

            sorgu = sorgu.filter(
                Kullanicilar.rol_id == rol_id_int
            )

        except ValueError:

            rol_id = ""

    # =====================================================
    # SONUÇLARI GETİR
    # =====================================================

    kullanicilar = sorgu.order_by(
        Kullanicilar.id.asc()
    ).all()

    # =====================================================
    # ROLLER
    # =====================================================

    roller = Rol.query.all()

    # =====================================================
    # SAYFAYA GÖNDER
    # =====================================================

    return render_template(
        "yonetici/kullanicilar.html",

        kullanicilar=kullanicilar,

        roller=roller,

        kullanici_adi=kullanici_adi,

        ad_soyad=ad_soyad,

        email=email,

        rol_id=rol_id
    )

# =========================================================
# YÖNETİCİ - ŞUBELER
# =========================================================

@main.route("/yonetici/subeler")
def yonetici_subeler():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    # =====================================================
    # FİLTRELER
    # =====================================================

    sube_ad = request.args.get(
        "sube_ad",
        ""
    ).strip()

    il = request.args.get(
        "il",
        ""
    ).strip()

    ilce = request.args.get(
        "ilce",
        ""
    ).strip()

    telefon = request.args.get(
        "telefon",
        ""
    ).strip()

    # =====================================================
    # ŞUBELER SORGUSU
    # =====================================================

    sorgu = Subeler.query

    # =====================================================
    # ŞUBE ADI
    # =====================================================

    if sube_ad:

        sorgu = sorgu.filter(
            Subeler.sube_ad.ilike(
                f"%{sube_ad}%"
            )
        )

    # =====================================================
    # İL
    # =====================================================

    if il:

        sorgu = sorgu.filter(
            Subeler.il.ilike(
                f"%{il}%"
            )
        )

    # =====================================================
    # İLÇE
    # =====================================================

    if ilce:

        sorgu = sorgu.filter(
            Subeler.ilce.ilike(
                f"%{ilce}%"
            )
        )

    # =====================================================
    # TELEFON
    # =====================================================

    if telefon:

        sorgu = sorgu.filter(
            Subeler.telefon.ilike(
                f"%{telefon}%"
            )
        )

    # =====================================================
    # SONUÇLARI GETİR
    # =====================================================

    subeler = sorgu.order_by(
        Subeler.id.asc()
    ).all()

    # =====================================================
    # SAYFAYA GÖNDER
    # =====================================================

    return render_template(
        "yonetici/subeler.html",

        subeler=subeler,

        sube_ad=sube_ad,

        il=il,

        ilce=ilce,

        telefon=telefon
    )
# =========================================================
# YÖNETİCİ - ŞUBE EKLE
# =========================================================

@main.route(
    "/yonetici/sube/ekle",
    methods=["GET", "POST"]
)
def yonetici_sube_ekle():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    if request.method == "POST":

        sube_ad = request.form.get(
            "sube_ad",
            ""
        ).strip()

        il = request.form.get(
            "il",
            ""
        ).strip()

        ilce = request.form.get(
            "ilce",
            ""
        ).strip()

        adres = request.form.get(
            "adres",
            ""
        ).strip()

        telefon = request.form.get(
            "telefon",
            ""
        ).strip()

        # =====================================================
        # ZORUNLU ALAN KONTROLLERİ
        # =====================================================

        if not sube_ad:

            flash(
                "Şube adı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_ekle.html"
            )

        if not il:

            flash(
                "İl alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_ekle.html"
            )

        if not ilce:

            flash(
                "İlçe alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_ekle.html"
            )

        if not adres:

            flash(
                "Adres alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_ekle.html"
            )

        if not telefon:

            flash(
                "Telefon alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_ekle.html"
            )

        # =====================================================
        # ŞUBE OLUŞTUR
        # =====================================================

        sube = Subeler(

            sube_ad=sube_ad,

            il=il,

            ilce=ilce,

            adres=adres,

            telefon=telefon

        )

        db.session.add(sube)

        db.session.commit()

        flash(
            "Şube başarıyla eklendi."
        )

        return redirect(
            url_for(
                "main.yonetici_subeler"
            )
        )

    return render_template(
        "yonetici/sube_ekle.html"
    )
# =========================================================
# YÖNETİCİ - ŞUBE DÜZENLE
# =========================================================

@main.route(
    "/yonetici/sube/<int:sube_id>/duzenle",
    methods=["GET", "POST"]
)
def yonetici_sube_duzenle(sube_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    # =====================================================
    # ŞUBEYİ BUL
    # =====================================================

    sube = Subeler.query.get(sube_id)

    if not sube:

        flash(
            "Düzenlemek istediğiniz şube bulunamadı."
        )

        return redirect(
            url_for("main.yonetici_subeler")
        )

    # =====================================================
    # FORM GÖNDERİLDİ
    # =====================================================

    if request.method == "POST":

        sube_ad = request.form.get(
            "sube_ad",
            ""
        ).strip()

        il = request.form.get(
            "il",
            ""
        ).strip()

        ilce = request.form.get(
            "ilce",
            ""
        ).strip()

        adres = request.form.get(
            "adres",
            ""
        ).strip()

        telefon = request.form.get(
            "telefon",
            ""
        ).strip()

        # =================================================
        # ZORUNLU ALAN KONTROLLERİ
        # =================================================

        if not sube_ad:

            flash(
                "Şube adı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_duzenle.html",
                sube=sube
            )

        if not il:

            flash(
                "İl alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_duzenle.html",
                sube=sube
            )

        if not ilce:

            flash(
                "İlçe alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_duzenle.html",
                sube=sube
            )

        if not adres:

            flash(
                "Adres alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_duzenle.html",
                sube=sube
            )

        if not telefon:

            flash(
                "Telefon alanı boş bırakılamaz."
            )

            return render_template(
                "yonetici/sube_duzenle.html",
                sube=sube
            )

        # =================================================
        # ŞUBE BİLGİLERİNİ GÜNCELLE
        # =================================================

        sube.sube_ad = sube_ad
        sube.il = il
        sube.ilce = ilce
        sube.adres = adres
        sube.telefon = telefon

        db.session.commit()

        flash(
            "Şube bilgileri başarıyla güncellendi."
        )

        return redirect(
            url_for(
                "main.yonetici_subeler"
            )
        )

    # =====================================================
    # GET → DÜZENLEME FORMUNU GÖSTER
    # =====================================================

    return render_template(
        "yonetici/sube_duzenle.html",
        sube=sube
    )

@main.route("/yonetici/sube-sil/<int:sube_id>", methods=["POST"])
def yonetici_sube_sil(sube_id):

    sube = Subeler.query.get_or_404(sube_id)

    try:

        db.session.delete(sube)
        db.session.commit()

        flash("Şube başarıyla silindi.", "success")

    except Exception:

        db.session.rollback()

        flash(
            "Şube silinemedi. Bu şubeye bağlı kayıtlar bulunuyor olabilir.",
            "danger"
        )

    return redirect(url_for("main.yonetici_subeler"))
# =========================================================
# YÖNETİCİ - KURYELER
# =========================================================

@main.route("/yonetici/kuryeler")
def yonetici_kuryeler():

    kullanici_adi = session.get("kullanici_adi")

    if not kullanici_adi:
        return redirect(url_for("main.yonetici_login"))

    # Filtre değerleri
    ad = request.args.get("ad", "").strip()
    soyad = request.args.get("soyad", "").strip()
    sube_id = request.args.get("sube_id", "").strip()
    telefon = request.args.get("telefon", "").strip()

    # Kuryeleri kullanıcı ve şube bilgileriyle birlikte getir
    query = Kuryeler.query.join(
        Kullanicilar,
        Kuryeler.kullanici_id == Kullanicilar.id
    ).join(
        Subeler,
        Kuryeler.sube_id == Subeler.id
    )

    # Filtreler
    if ad:
        query = query.filter(
            Kullanicilar.ad.ilike(f"%{ad}%")
        )

    if soyad:
        query = query.filter(
            Kullanicilar.soyad.ilike(f"%{soyad}%")
        )

    if sube_id:
        query = query.filter(
            Kuryeler.sube_id == sube_id
        )

    if telefon:
        query = query.filter(
            Kuryeler.telefon.ilike(f"%{telefon}%")
        )

    kuryeler = query.all()

    subeler = Subeler.query.order_by(
        Subeler.sube_ad
    ).all()

    return render_template(
        "yonetici/kuryeler.html",
        kuryeler=kuryeler,
        subeler=subeler,
        ad=ad,
        soyad=soyad,
        sube_id=sube_id,
        telefon=telefon
    )


# =========================================================
# YÖNETİCİ - KURYE PERFORMANSI
# =========================================================

@main.route("/yonetici/kurye-performans")
def yonetici_kurye_performans():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    performanslar = kurye_performanslarini_getir()

    return render_template(
        "yonetici/kurye_performans.html",
        performanslar=performanslar
    )
# =========================================================
# KURYE PERFORMANS VERİLERİ
# =========================================================

def kurye_performanslarini_getir():

    kuryeler = Kuryeler.query.order_by(
        Kuryeler.id.asc()
    ).all()

    performanslar = []

    for kurye in kuryeler:

        toplam_kargo = Kargolar.query.filter_by(
            kurye_id=kurye.id
        ).count()

        teslim_edilen = Kargolar.query.filter_by(
            kurye_id=kurye.id,
            durum="Teslim Edildi"
        ).count()

        dagitimda = Kargolar.query.filter_by(
            kurye_id=kurye.id,
            durum="Dağıtımda"
        ).count()

        bekleyen = Kargolar.query.filter(
            Kargolar.kurye_id == kurye.id,
            Kargolar.durum.not_in([
                "Teslim Edildi",
                "İptal Edildi"
            ])
        ).count()

        # =============================================
        # TESLİMAT ORANI
        # =============================================

        if toplam_kargo > 0:

            teslimat_orani = round(
                (
                    teslim_edilen /
                    toplam_kargo
                ) * 100,
                2
            )

        else:

            teslimat_orani = 0


        # =============================================
        # ORTALAMA TESLİMAT SÜRESİ
        # =============================================

        teslim_edilen_kargolar = Kargolar.query.filter(
            Kargolar.kurye_id == kurye.id,
            Kargolar.durum == "Teslim Edildi",
            Kargolar.gonderim_tarihi.isnot(None),
            Kargolar.teslim_tarihi.isnot(None)
        ).all()

        teslim_sureleri = []

        for kargo in teslim_edilen_kargolar:

            fark = (
                kargo.teslim_tarihi -
                kargo.gonderim_tarihi
            )

            teslim_sureleri.append(
                fark.total_seconds()
            )

        if teslim_sureleri:

            ortalama_saniye = (
                sum(teslim_sureleri) /
                len(teslim_sureleri)
            )

            ortalama_saat = round(
                ortalama_saniye / 3600,
                1
            )

        else:

            ortalama_saat = 0


        performanslar.append({

            "kurye": kurye,

            "toplam_kargo": toplam_kargo,

            "teslim_edilen": teslim_edilen,

            "dagitimda": dagitimda,

            "bekleyen": bekleyen,

            "teslimat_orani": teslimat_orani,

            "ortalama_saat": ortalama_saat

        })

    return performanslar
# =========================================================
# YENİ KURYE EKLE
# =========================================================

@main.route("/yonetici/kurye/ekle", methods=["GET", "POST"])
def yonetici_kurye_ekle():

    kullanici_adi = session.get("kullanici_adi")

    if not kullanici_adi:
        return redirect(url_for("main.yonetici_login"))

    subeler = Subeler.query.order_by(
        Subeler.sube_ad
    ).all()

    if request.method == "POST":

        ad = request.form.get("ad", "").strip()
        soyad = request.form.get("soyad", "").strip()
        kullanici_adi_form = request.form.get(
            "kullanici_adi",
            ""
        ).strip()
        email = request.form.get("email", "").strip()
        sifre = request.form.get("sifre", "").strip()
        telefon = request.form.get("telefon", "").strip()
        sube_id = request.form.get("sube_id", "").strip()

        # Boş alan kontrolü
        if not all([
            ad,
            soyad,
            kullanici_adi_form,
            email,
            sifre,
            telefon,
            sube_id
        ]):

            flash(
                "Lütfen tüm alanları doldurunuz.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_ekle.html",
                subeler=subeler
            )

        # Kullanıcı adı kontrolü
        mevcut_kullanici = Kullanicilar.query.filter_by(
            kullanici_adi=kullanici_adi_form
        ).first()

        if mevcut_kullanici:

            flash(
                "Bu kullanıcı adı zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_ekle.html",
                subeler=subeler
            )

        # Email kontrolü
        mevcut_email = Kullanicilar.query.filter_by(
            email=email
        ).first()

        if mevcut_email:

            flash(
                "Bu email adresi zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_ekle.html",
                subeler=subeler
            )

        # Kurye rolünü bul
        kurye_rolu = Rol.query.filter_by(
            ad="Kurye"
        ).first()

        if not kurye_rolu:

            flash(
                "Kurye rolü bulunamadı.",
                "danger"
            )

            return redirect(
                url_for("main.yonetici_kuryeler")
            )

        # Kullanıcı oluştur
        yeni_kullanici = Kullanicilar(
            rol_id=kurye_rolu.id,
            sifre=sifre,
            ad=ad,
            soyad=soyad,
            kullanici_adi=kullanici_adi_form,
            email=email,
            telefon=telefon
        )

        db.session.add(yeni_kullanici)

        db.session.flush()

        # Kurye oluştur
        yeni_kurye = Kuryeler(
            kullanici_id=yeni_kullanici.id,
            sube_id=int(sube_id),
            telefon=telefon
        )

        db.session.add(yeni_kurye)

        db.session.commit()

        flash(
            "Kurye başarıyla eklendi.",
            "success"
        )

        return redirect(
            url_for("main.yonetici_kuryeler")
        )

    return render_template(
        "yonetici/kurye_ekle.html",
        subeler=subeler
    )


# =========================================================
# KURYE DÜZENLE
# =========================================================

@main.route(
    "/yonetici/kurye/duzenle/<int:kurye_id>",
    methods=["GET", "POST"]
)
def yonetici_kurye_duzenle(kurye_id):

    kullanici_adi = session.get("kullanici_adi")

    if not kullanici_adi:
        return redirect(
            url_for("main.yonetici_login")
        )

    kurye = Kuryeler.query.get_or_404(kurye_id)

    kullanici = Kullanicilar.query.get_or_404(
        kurye.kullanici_id
    )

    subeler = Subeler.query.order_by(
        Subeler.sube_ad
    ).all()

    if request.method == "POST":

        ad = request.form.get(
            "ad",
            ""
        ).strip()

        soyad = request.form.get(
            "soyad",
            ""
        ).strip()

        yeni_kullanici_adi = request.form.get(
            "kullanici_adi",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        telefon = request.form.get(
            "telefon",
            ""
        ).strip()

        sube_id = request.form.get(
            "sube_id",
            ""
        ).strip()

        sifre = request.form.get(
            "sifre",
            ""
        ).strip()

        # Zorunlu alan kontrolü
        if not all([
            ad,
            soyad,
            yeni_kullanici_adi,
            email,
            telefon,
            sube_id
        ]):

            flash(
                "Lütfen zorunlu alanları doldurunuz.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_duzenle.html",
                kurye=kurye,
                kullanici=kullanici,
                subeler=subeler
            )

        # Kullanıcı adı başka bir kullanıcıda var mı?
        mevcut_kullanici = Kullanicilar.query.filter(
            Kullanicilar.kullanici_adi == yeni_kullanici_adi,
            Kullanicilar.id != kullanici.id
        ).first()

        if mevcut_kullanici:

            flash(
                "Bu kullanıcı adı zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_duzenle.html",
                kurye=kurye,
                kullanici=kullanici,
                subeler=subeler
            )

        # Email başka kullanıcıda var mı?
        mevcut_email = Kullanicilar.query.filter(
            Kullanicilar.email == email,
            Kullanicilar.id != kullanici.id
        ).first()

        if mevcut_email:

            flash(
                "Bu email adresi zaten kullanılıyor.",
                "danger"
            )

            return render_template(
                "yonetici/kurye_duzenle.html",
                kurye=kurye,
                kullanici=kullanici,
                subeler=subeler
            )

        # Kullanıcı bilgilerini güncelle
        kullanici.ad = ad
        kullanici.soyad = soyad
        kullanici.kullanici_adi = yeni_kullanici_adi
        kullanici.email = email
        kullanici.telefon = telefon

        # Şifre girilmişse değiştir
        if sifre:
            kullanici.sifre = sifre

        # Kurye bilgilerini güncelle
        kurye.telefon = telefon
        kurye.sube_id = int(sube_id)

        db.session.commit()

        flash(
            "Kurye bilgileri başarıyla güncellendi.",
            "success"
        )

        return redirect(
            url_for("main.yonetici_kuryeler")
        )

    return render_template(
        "yonetici/kurye_duzenle.html",
        kurye=kurye,
        kullanici=kullanici,
        subeler=subeler
    )


# =========================================================
# KURYE SİL
# =========================================================

@main.route(
    "/yonetici/kurye/sil/<int:kurye_id>",
    methods=["POST"]
)
def yonetici_kurye_sil(kurye_id):

    kullanici_adi = session.get("kullanici_adi")

    if not kullanici_adi:
        return redirect(
            url_for("main.yonetici_login")
        )

    kurye = Kuryeler.query.get_or_404(kurye_id)

    # Kuryeye bağlı kargo var mı?
    kargo_sayisi = Kargolar.query.filter_by(
        kurye_id=kurye.id
    ).count()

    if kargo_sayisi > 0:

        flash(
            "Bu kuryeye atanmış kargolar bulunduğu için "
            "kurye silinemez.",
            "danger"
        )

        return redirect(
            url_for("main.yonetici_kuryeler")
        )

    # Kullanıcı kaydını bul
    kullanici = Kullanicilar.query.get(
        kurye.kullanici_id
    )

    # Önce kurye kaydını sil
    db.session.delete(kurye)

    # Kullanıcı kaydını da sil
    if kullanici:
        db.session.delete(kullanici)

    db.session.commit()

    flash(
        "Kurye başarıyla silindi.",
        "success"
    )

    return redirect(
        url_for("main.yonetici_kuryeler")
    )

# =========================================================
# YÖNETİCİ - KARGOLAR
# =========================================================

@main.route("/yonetici/kargolar")
def yonetici_kargolar():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    # =====================================================
    # FİLTRELER
    # =====================================================

    takip_no = request.args.get("takip_no", "").strip()
    gonderici = request.args.get("gonderici", "").strip()
    alici = request.args.get("alici", "").strip()
    durum = request.args.get("durum", "").strip()
    sube_id = request.args.get("sube_id", "").strip()
    kurye_id = request.args.get("kurye_id", "").strip()

    query = Kargolar.query

    if takip_no:
        query = query.filter(
            Kargolar.takip_no.ilike(f"%{takip_no}%")
        )

    if gonderici:
        query = query.filter(
            Kargolar.gonderici.ilike(f"%{gonderici}%")
        )

    if alici:
        query = query.filter(
            Kargolar.alici.ilike(f"%{alici}%")
        )

    if durum:
        query = query.filter(
            Kargolar.durum == durum
        )

    if sube_id:
        query = query.filter(
            Kargolar.sube_id == int(sube_id)
        )

    if kurye_id:
        query = query.filter(
            Kargolar.kurye_id == int(kurye_id)
        )

    kargolar = query.order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

    subeler = Subeler.query.order_by(
        Subeler.sube_ad
    ).all()

    kuryeler = Kuryeler.query.join(
        Kullanicilar,
        Kuryeler.kullanici_id == Kullanicilar.id
    ).order_by(
        Kullanicilar.ad,
        Kullanicilar.soyad
    ).all()

    durumlar = [
        "Hazırlanıyor",
        "Şubede",
        "Dağıtımda",
        "Teslim Edildi",
        "İptal Edildi"
    ]

    return render_template(
        "yonetici/kargolar.html",
        kargolar=kargolar,
        subeler=subeler,
        kuryeler=kuryeler,
        durumlar=durumlar,
        takip_no=takip_no,
        gonderici=gonderici,
        alici=alici,
        durum=durum,
        sube_id=sube_id,
        kurye_id=kurye_id
    )
# =========================================================
# YÖNETİCİ - KARGO EKLE
# =========================================================

@main.route(
    "/yonetici/kargo/ekle",
    methods=["GET", "POST"]
)
def yonetici_kargo_ekle():

    if not giris_kontrolu():
        return redirect(url_for("main.yonetici_login"))

    if not rol_kontrolu("Yönetici"):
        return redirect(url_for("main.index"))

    kullanicilar = (
        Kullanicilar.query
        .order_by(Kullanicilar.ad, Kullanicilar.soyad)
        .all()
    )

    subeler = (
        Subeler.query
        .filter_by(aktif=True)
        .order_by(Subeler.sube_ad)
        .all()
    )

    kargo_turleri = (
        KargoTurleri.query
        .filter_by(aktif=True)
        .order_by(KargoTurleri.id)
        .all()
    )

    def formu_goster():
        return render_template(
            "yonetici/kargo_ekle.html",
            kullanicilar=kullanicilar,
            subeler=subeler,
            kargo_turleri=kargo_turleri
        )

    if request.method == "POST":

        gonderici_id = request.form.get("gonderici_id", type=int)
        alici_id = request.form.get("alici_id", type=int)
        sube_id = request.form.get("sube_id", type=int)
        kargo_turu_id = request.form.get("kargo_turu_id", type=int)

        agirlik = request.form.get("agirlik", "").strip()
        desi_en = request.form.get("desi_en", "").strip()
        desi_boy = request.form.get("desi_boy", "").strip()
        desi_yukseklik = request.form.get("desi_yukseklik", "").strip()

        if not all([
            gonderici_id,
            alici_id,
            sube_id,
            kargo_turu_id,
            agirlik,
            desi_en,
            desi_boy,
            desi_yukseklik
        ]):
            flash("Lütfen tüm alanları doldurunuz.", "danger")
            return formu_goster()

        gonderici_kullanici = Kullanicilar.query.get(gonderici_id)
        alici_kullanici = Kullanicilar.query.get(alici_id)

        if not gonderici_kullanici:
            flash("Seçilen gönderici bulunamadı.", "danger")
            return formu_goster()

        if not alici_kullanici:
            flash("Seçilen alıcı bulunamadı.", "danger")
            return formu_goster()

        if gonderici_kullanici.id == alici_kullanici.id:
            flash("Gönderici ve alıcı aynı kişi olamaz.", "danger")
            return formu_goster()

        sube = Subeler.query.filter_by(
            id=sube_id,
            aktif=True
        ).first()

        if not sube:
            flash("Seçilen şube bulunamadı.", "danger")
            return formu_goster()

        if not gonderici_kullanici.adres:
            flash("Seçilen göndericinin adres bilgisi bulunmuyor.", "danger")
            return formu_goster()

        # Yönetici de yalnızca göndericinin şehrindeki şubeden kargo oluşturabilir.
        if not adres_sube_uyumlu_mu(gonderici_kullanici.adres, sube):
            flash(
                "Seçilen şube, göndericinin adresinin bulunduğu şehirde değil.",
                "danger"
            )
            return formu_goster()

        kargo_turu = KargoTurleri.query.filter_by(
            id=kargo_turu_id,
            aktif=True
        ).first()

        if not kargo_turu:
            flash("Seçilen kargo türü bulunamadı.", "danger")
            return formu_goster()

        try:
            agirlik = float(agirlik)
            desi_en = float(desi_en)
            desi_boy = float(desi_boy)
            desi_yukseklik = float(desi_yukseklik)

            if agirlik <= 0 or desi_en <= 0 or desi_boy <= 0 or desi_yukseklik <= 0:
                raise ValueError

        except (ValueError, TypeError):
            flash("Ağırlık ve ölçü bilgilerini doğru giriniz.", "danger")
            return formu_goster()

        if not gonderici_kullanici.telefon:
            flash("Seçilen göndericinin telefon bilgisi bulunmuyor.", "danger")
            return formu_goster()

        if not alici_kullanici.telefon:
            flash("Seçilen alıcının telefon bilgisi bulunmuyor.", "danger")
            return formu_goster()

        if not alici_kullanici.adres:
            flash("Seçilen alıcının adres bilgisi bulunmuyor.", "danger")
            return formu_goster()

        desi = (desi_en * desi_boy * desi_yukseklik) / 3000

        _, _, _, ucret = kargo_ucreti_hesapla(
            agirlik,
            desi,
            kargo_turu
        )

        from uuid import uuid4

        takip_no = "KT" + uuid4().hex[:10].upper()

        while Kargolar.query.filter_by(takip_no=takip_no).first():
            takip_no = "KT" + uuid4().hex[:10].upper()

        durum = "Hazırlanıyor"
        gonderim_tarihi = datetime.now()

        yeni_kargo = Kargolar(
            takip_no=takip_no,
            gonderici_id=gonderici_kullanici.id,
            gonderici=f"{gonderici_kullanici.ad} {gonderici_kullanici.soyad}",
            gonderici_telefon=gonderici_kullanici.telefon,
            gonderici_adres=gonderici_kullanici.adres,
            alici_id=alici_kullanici.id,
            alici=f"{alici_kullanici.ad} {alici_kullanici.soyad}",
            alici_telefon=alici_kullanici.telefon,
            alici_adres=alici_kullanici.adres,
            kargo_turu_id=kargo_turu.id,
            durum=durum,
            agirlik=agirlik,
            desi=round(desi, 2),
            ucret=ucret,
            gonderim_tarihi=gonderim_tarihi,
            teslim_tarihi=None,
            sube_id=sube.id,
            kurye_id=None
        )

        try:
            db.session.add(yeni_kargo)
            db.session.flush()

            hareket = Kargo_Hareketleri(
                kargo_id=yeni_kargo.id,
                sube_id=sube.id,
                kurye_id=None,
                durum=durum,
                aciklama=(
                    f"Kargo {sube.sube_ad} şubesinde "
                    f"{kargo_turu.ad} gönderi olarak oluşturuldu."
                ),
                tarih=datetime.now()
            )

            db.session.add(hareket)
            db.session.commit()

        except Exception:
            db.session.rollback()
            flash("Kargo oluşturulurken bir hata oluştu.", "danger")
            return formu_goster()

        flash(
            f"Kargo başarıyla oluşturuldu. "
            f"Takip numarası: {takip_no} | "
            f"Toplam ücret: {ucret:.2f} ₺",
            "success"
        )

        return redirect(url_for("main.yonetici_kargolar"))

    return formu_goster()

@main.route(
    "/yonetici/kargo/<int:kargo_id>"
)
def yonetici_kargo_detay(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    kargo = Kargolar.query.get_or_404(
        kargo_id
    )

    hareketler = Kargo_Hareketleri.query.filter_by(
        kargo_id=kargo.id
    ).order_by(
        Kargo_Hareketleri.tarih.desc()
    ).all()

    return render_template(
        "yonetici/kargo_detay.html",
        kargo=kargo,
        hareketler=hareketler
    )


# =========================================================
# YÖNETİCİ - KARGO DÜZENLE
# =========================================================

@main.route(
    "/yonetici/kargo/duzenle/<int:kargo_id>",
    methods=["GET", "POST"]
)
def yonetici_kargo_duzenle(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    kargo = Kargolar.query.get_or_404(
        kargo_id
    )

    subeler = Subeler.query.order_by(
        Subeler.sube_ad
    ).all()

    kuryeler = Kuryeler.query.join(
        Kullanicilar,
        Kuryeler.kullanici_id == Kullanicilar.id
    ).order_by(
        Kullanicilar.ad,
        Kullanicilar.soyad
    ).all()

    durumlar = [
        "Hazırlanıyor",
        "Şubede",
        "Dağıtımda",
        "Teslim Edildi",
        "İptal Edildi"
    ]

    if request.method == "POST":

        kargo.takip_no = request.form.get(
            "takip_no",
            ""
        ).strip()

        kargo.gonderici = request.form.get(
            "gonderici",
            ""
        ).strip()

        kargo.gonderici_telefon = request.form.get(
            "gonderici_telefon",
            ""
        ).strip()

        kargo.gonderici_adres = request.form.get(
            "gonderici_adres",
            ""
        ).strip()

        kargo.alici = request.form.get(
            "alici",
            ""
        ).strip()

        kargo.alici_telefon = request.form.get(
            "alici_telefon",
            ""
        ).strip()

        kargo.alici_adres = request.form.get(
            "alici_adres",
            ""
        ).strip()

        kargo.durum = request.form.get(
            "durum",
            ""
        ).strip()

        kargo.agirlik = request.form.get(
            "agirlik",
            ""
        ).strip()

        kargo.ucret = request.form.get(
            "ucret",
            ""
        ).strip()

        gonderim_tarihi = request.form.get(
            "gonderim_tarihi",
            ""
        ).strip()

        teslim_tarihi = request.form.get(
            "teslim_tarihi",
            ""
        ).strip()

        kargo.sube_id = int(
            request.form.get("sube_id")
        )

        kurye_id = request.form.get(
            "kurye_id",
            ""
        ).strip()

        kargo.kurye_id = (
            int(kurye_id)
            if kurye_id
            else None
        )

        try:

            kargo.gonderim_tarihi = datetime.strptime(
                gonderim_tarihi,
                "%Y-%m-%dT%H:%M"
            )

            if teslim_tarihi:

                kargo.teslim_tarihi = datetime.strptime(
                    teslim_tarihi,
                    "%Y-%m-%dT%H:%M"
                )

            else:

                kargo.teslim_tarihi = None

        except ValueError:

            flash(
                "Tarih formatı geçersiz.",
                "danger"
            )

            return render_template(
                "yonetici/kargo_duzenle.html",
                kargo=kargo,
                subeler=subeler,
                kuryeler=kuryeler,
                durumlar=durumlar
            )

        # Takip numarası başka kargoda kullanılıyor mu?
        mevcut_kargo = Kargolar.query.filter(
            Kargolar.takip_no == kargo.takip_no,
            Kargolar.id != kargo.id
        ).first()

        if mevcut_kargo:

            flash(
                "Bu takip numarası başka bir kargoda kullanılıyor.",
                "danger"
            )

            return render_template(
                "yonetici/kargo_duzenle.html",
                kargo=kargo,
                subeler=subeler,
                kuryeler=kuryeler,
                durumlar=durumlar
            )

        db.session.commit()

        flash(
            "Kargo bilgileri başarıyla güncellendi.",
            "success"
        )

        return redirect(
            url_for(
                "main.yonetici_kargolar"
            )
        )

    return render_template(
        "yonetici/kargo_duzenle.html",
        kargo=kargo,
        subeler=subeler,
        kuryeler=kuryeler,
        durumlar=durumlar
    )


# =========================================================
# YÖNETİCİ - KARGO SİL
# =========================================================

@main.route(
    "/yonetici/kargo/sil/<int:kargo_id>",
    methods=["POST"]
)
def yonetici_kargo_sil(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    kargo = Kargolar.query.get_or_404(
        kargo_id
    )

    # Önce kargoya bağlı hareketleri sil
    hareketler = Kargo_Hareketleri.query.filter_by(
        kargo_id=kargo.id
    ).all()

    for hareket in hareketler:
        db.session.delete(hareket)

    # Daha sonra kargoyu sil
    db.session.delete(kargo)

    db.session.commit()

    flash(
        "Kargo başarıyla silindi.",
        "success"
    )

    return redirect(
        url_for("main.yonetici_kargolar")
    )
# =========================================================
# YÖNETİCİ - MÜŞTERİ DEĞERLENDİRMELERİ
# =========================================================

@main.route("/yonetici/degerlendirmeler")
def yonetici_degerlendirmeler():

    if not giris_kontrolu():
        return redirect(
            url_for("main.yonetici_login")
        )

    if not rol_kontrolu("Yönetici"):
        return redirect(
            url_for("main.index")
        )

    # =====================================================
    # FİLTRELER
    # =====================================================

    arama = request.args.get(
        "arama",
        ""
    ).strip()

    puan_filtresi = request.args.get(
        "puan",
        type=int
    )

    # =====================================================
    # TÜM DEĞERLENDİRMELER
    # İstatistikler filtrelerden etkilenmez.
    # =====================================================

    tum_degerlendirmeler = (
        Degerlendirmeler.query
        .order_by(
            Degerlendirmeler.tarih.desc()
        )
        .all()
    )

    toplam_degerlendirme = len(
        tum_degerlendirmeler
    )

    if toplam_degerlendirme > 0:

        ortalama_puan = round(
            sum(
                d.puan
                for d in tum_degerlendirmeler
            ) / toplam_degerlendirme,
            1
        )

        olumlu_degerlendirme = sum(
            1
            for d in tum_degerlendirmeler
            if d.puan >= 4
        )

        olumlu_oran = round(
            (
                olumlu_degerlendirme /
                toplam_degerlendirme
            ) * 100,
            1
        )

    else:

        ortalama_puan = 0
        olumlu_oran = 0


    yorum_sayisi = sum(
        1
        for d in tum_degerlendirmeler
        if d.yorum
    )


    puan_dagilimi = {
        5: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 0
    }

    for degerlendirme in tum_degerlendirmeler:

        if degerlendirme.puan in puan_dagilimi:
            puan_dagilimi[
                degerlendirme.puan
            ] += 1


    puan_yuzdeleri = {}

    for puan, adet in puan_dagilimi.items():

        if toplam_degerlendirme > 0:

            puan_yuzdeleri[puan] = round(
                (
                    adet /
                    toplam_degerlendirme
                ) * 100,
                1
            )

        else:
            puan_yuzdeleri[puan] = 0


    # =====================================================
    # SAYFADA GÖSTERİLECEK SATIRLAR
    # =====================================================

    degerlendirme_satirlari = []

    # Şube / kurye ortalamaları için geçici yapılar
    sube_puanlari = {}
    kurye_puanlari = {}


    for degerlendirme in tum_degerlendirmeler:

        kullanici = Kullanicilar.query.get(
            degerlendirme.kullanici_id
        )

        kargo = Kargolar.query.get(
            degerlendirme.kargo_id
        )

        sube = None
        kurye = None

        if kargo:

            if kargo.sube_id:
                sube = Subeler.query.get(
                    kargo.sube_id
                )

            if kargo.kurye_id:
                kurye = Kuryeler.query.get(
                    kargo.kurye_id
                )


        musteri_adi = "Silinmiş kullanıcı"

        if kullanici:
            musteri_adi = (
                f"{kullanici.ad} "
                f"{kullanici.soyad}"
            )


        takip_no = (
            kargo.takip_no
            if kargo
            else "-"
        )

        sube_adi = (
            sube.sube_ad
            if sube
            else "-"
        )

        kurye_adi = "-"

        if kurye and kurye.kullanici:
            kurye_adi = (
                f"{kurye.kullanici.ad} "
                f"{kurye.kullanici.soyad}"
            )


        # =============================================
        # ŞUBE PUANLARI
        # =============================================

        if sube:

            if sube.id not in sube_puanlari:
                sube_puanlari[sube.id] = {
                    "sube_ad": sube.sube_ad,
                    "toplam_puan": 0,
                    "degerlendirme_sayisi": 0
                }

            sube_puanlari[sube.id][
                "toplam_puan"
            ] += degerlendirme.puan

            sube_puanlari[sube.id][
                "degerlendirme_sayisi"
            ] += 1


        # =============================================
        # KURYE PUANLARI
        # =============================================

        if kurye and kurye.kullanici:

            if kurye.id not in kurye_puanlari:
                kurye_puanlari[kurye.id] = {
                    "kurye_ad": kurye_adi,
                    "toplam_puan": 0,
                    "degerlendirme_sayisi": 0
                }

            kurye_puanlari[kurye.id][
                "toplam_puan"
            ] += degerlendirme.puan

            kurye_puanlari[kurye.id][
                "degerlendirme_sayisi"
            ] += 1


        satir = {
            "id": degerlendirme.id,
            "puan": degerlendirme.puan,
            "yorum": degerlendirme.yorum,
            "tarih": degerlendirme.tarih,
            "musteri_adi": musteri_adi,
            "takip_no": takip_no,
            "kargo_id": (
                kargo.id
                if kargo
                else None
            ),
            "sube_adi": sube_adi,
            "kurye_adi": kurye_adi
        }


        # =============================================
        # PUAN FİLTRESİ
        # =============================================

        if (
            puan_filtresi in [1, 2, 3, 4, 5]
            and degerlendirme.puan != puan_filtresi
        ):
            continue


        # =============================================
        # ARAMA FİLTRESİ
        # =============================================

        if arama:

            aranacak_metin = " ".join([
                musteri_adi,
                takip_no,
                sube_adi,
                kurye_adi,
                degerlendirme.yorum or ""
            ]).lower()

            if arama.lower() not in aranacak_metin:
                continue


        degerlendirme_satirlari.append(
            satir
        )


    # =====================================================
    # ŞUBE ORTALAMALARI
    # =====================================================

    sube_istatistikleri = []

    for veri in sube_puanlari.values():

        ortalama = round(
            veri["toplam_puan"] /
            veri["degerlendirme_sayisi"],
            1
        )

        sube_istatistikleri.append({
            "sube_ad": veri["sube_ad"],
            "ortalama_puan": ortalama,
            "degerlendirme_sayisi": (
                veri["degerlendirme_sayisi"]
            )
        })


    sube_istatistikleri.sort(
        key=lambda x: (
            x["ortalama_puan"],
            x["degerlendirme_sayisi"]
        ),
        reverse=True
    )


    # =====================================================
    # KURYE ORTALAMALARI
    # =====================================================

    kurye_istatistikleri = []

    for veri in kurye_puanlari.values():

        ortalama = round(
            veri["toplam_puan"] /
            veri["degerlendirme_sayisi"],
            1
        )

        kurye_istatistikleri.append({
            "kurye_ad": veri["kurye_ad"],
            "ortalama_puan": ortalama,
            "degerlendirme_sayisi": (
                veri["degerlendirme_sayisi"]
            )
        })


    kurye_istatistikleri.sort(
        key=lambda x: (
            x["ortalama_puan"],
            x["degerlendirme_sayisi"]
        ),
        reverse=True
    )


    return render_template(
        "yonetici/degerlendirmeler.html",
        degerlendirmeler=degerlendirme_satirlari,
        toplam_degerlendirme=toplam_degerlendirme,
        ortalama_puan=ortalama_puan,
        olumlu_oran=olumlu_oran,
        yorum_sayisi=yorum_sayisi,
        puan_dagilimi=puan_dagilimi,
        puan_yuzdeleri=puan_yuzdeleri,
        sube_istatistikleri=sube_istatistikleri,
        kurye_istatistikleri=kurye_istatistikleri,
        arama=arama,
        puan_filtresi=puan_filtresi
    )

# =========================================================
# PERSONEL GİRİŞİ
# =========================================================

@main.route("/personel_login", methods=["GET", "POST"])
def personel_login():

    # Login ekranına gelindiğinde mevcut kullanıcı oturumunu temizle
    session.pop("kullanici_id", None)
    session.pop("rol", None)
    session.pop("kullanici_adi", None)
    session.pop("personel_id", None)
    session.pop("kurye_id", None)
    session.pop("sube_id", None)

    if request.method == "POST":

        email = request.form.get("email")
        sifre = request.form.get("sifre")
        personel_turu = request.form.get("personel_turu")

        kullanici = Kullanicilar.query.filter_by(
            email=email
        ).first()

        if not kullanici or not check_password_hash(
            kullanici.sifre,
            sifre
        ):
            flash("E-posta veya şifre hatalı.")
            return render_template(
                "login/personel_login.html"
            )

        if personel_turu == "sube":

            if kullanici.rol.ad != "Şube Personeli":
                flash("Bu hesap şube personeli hesabı değil.")
                return render_template(
                    "login/personel_login.html"
                )

            personel = SubePersonelleri.query.filter_by(
                kullanici_id=kullanici.id
            ).first()

            if not personel:
                flash("Bu kullanıcı herhangi bir şubeye atanmamış.")
                return render_template(
                    "login/personel_login.html"
                )

            if not personel.aktif:
                flash("Personel hesabınız aktif değil.")
                return render_template(
                    "login/personel_login.html"
                )

            session["kullanici_id"] = kullanici.id
            session["rol"] = kullanici.rol.ad
            session["kullanici_adi"] = kullanici.kullanici_adi
            session["personel_id"] = personel.id
            session["sube_id"] = personel.sube_id

            return redirect(
                url_for("main.subepersoneli_panel")
            )

        elif personel_turu == "kurye":

            if kullanici.rol.ad != "Kurye":
                flash("Bu hesap kurye hesabı değil.")
                return render_template(
                    "login/personel_login.html"
                )

            kurye = Kuryeler.query.filter_by(
                kullanici_id=kullanici.id
            ).first()

            if not kurye:
                flash("Kurye bilgileri bulunamadı.")
                return render_template(
                    "login/personel_login.html"
                )

            session["kullanici_id"] = kullanici.id
            session["rol"] = kullanici.rol.ad
            session["kullanici_adi"] = kullanici.kullanici_adi
            session["kurye_id"] = kurye.id
            session["sube_id"] = kurye.sube_id

            return redirect(
                url_for("main.kurye_panel")
            )

        else:

            flash("Lütfen personel türünü seçiniz.")

    return render_template(
        "login/personel_login.html"
    )
# =========================================================
# ŞUBE PERSONELİ PANELİ
# =========================================================

@main.route("/subepersoneli_panel")
def subepersoneli_panel():

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Şube Personeli"):
        return redirect(
            url_for("main.index")
        )

    personel = sube_personelini_getir()

    if not personel:

        flash(
            "Personel bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    if not personel.aktif:

        flash(
            "Personel hesabınız aktif değil."
        )

        return redirect(
            url_for("main.personel_login")
        )

    sube = Subeler.query.get(
        personel.sube_id
    )

    if not sube:

        flash(
            "Bağlı olduğunuz şube bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargolar = Kargolar.query.filter_by(
        sube_id=sube.id
    ).order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

    return render_template(
        "panel/sube_personel_panel.html",
        personel=personel,
        kullanici=personel.kullanici,
        sube=sube,
        kargolar=kargolar,
        toplam_kargo=len(kargolar),
        bekleyen_kargo=Kargolar.query.filter(
            Kargolar.sube_id == sube.id,
            Kargolar.durum != "Teslim Edildi"
        ).count(),
        teslim_edilen_kargo=Kargolar.query.filter_by(
            sube_id=sube.id,
            durum="Teslim Edildi"
        ).count(),
        kurye_atanan_kargo=Kargolar.query.filter(
            Kargolar.sube_id == sube.id,
            Kargolar.kurye_id.isnot(None)
        ).count()
    )


# =========================================================
# ŞUBE PERSONELİ - KARGOLAR
# =========================================================

@main.route("/subepersoneli/kargolar")
def subepersoneli_kargolar():

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Şube Personeli"):
        return redirect(
            url_for("main.index")
        )

    personel = sube_personelini_getir()

    if not personel or not personel.aktif:

        flash(
            "Personel hesabınız aktif değil."
        )

        return redirect(
            url_for("main.personel_login")
        )

    sube = Subeler.query.get(
        personel.sube_id
    )

    if not sube:

        flash(
            "Bağlı olduğunuz şube bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    # =====================================================
    # FİLTRELER
    # =====================================================

    takip_no = request.args.get(
        "takip_no",
        ""
    ).strip()

    gonderici = request.args.get(
        "gonderici",
        ""
    ).strip()

    alici = request.args.get(
        "alici",
        ""
    ).strip()

    durum = request.args.get(
        "durum",
        ""
    ).strip()

    kurye_id = request.args.get(
        "kurye_id",
        ""
    ).strip()

    tarih = request.args.get(
        "tarih",
        ""
    ).strip()

    # =====================================================
    # KARGOLAR SORGUSU
    # =====================================================

    sorgu = Kargolar.query.filter_by(
        sube_id=sube.id
    )

    # =====================================================
    # TAKİP NUMARASI
    # =====================================================

    if takip_no:

        sorgu = sorgu.filter(
            Kargolar.takip_no.ilike(
                f"%{takip_no}%"
            )
        )

    # =====================================================
    # GÖNDERİCİ
    # =====================================================

    if gonderici:

        sorgu = sorgu.filter(
            Kargolar.gonderici.ilike(
                f"%{gonderici}%"
            )
        )

    # =====================================================
    # ALICI
    # =====================================================

    if alici:

        sorgu = sorgu.filter(
            Kargolar.alici.ilike(
                f"%{alici}%"
            )
        )

    # =====================================================
    # DURUM
    # =====================================================

    if durum:

        sorgu = sorgu.filter(
            Kargolar.durum == durum
        )

    # =====================================================
    # KURYE
    # =====================================================

    if kurye_id:

        try:

            kurye_id_int = int(kurye_id)

            sorgu = sorgu.filter(
                Kargolar.kurye_id == kurye_id_int
            )

        except ValueError:

            kurye_id = ""

    # =====================================================
    # TARİH
    # =====================================================

    if tarih:

        try:

            secilen_tarih = datetime.strptime(
                tarih,
                "%Y-%m-%d"
            )

            ertesi_gun = secilen_tarih.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            sonraki_gun = ertesi_gun + timedelta(days=1)

            sorgu = sorgu.filter(
                Kargolar.gonderim_tarihi >= ertesi_gun,
                Kargolar.gonderim_tarihi < sonraki_gun
            )

        except ValueError:

            tarih = ""

    # =====================================================
    # SONUÇLARI GETİR
    # =====================================================

    kargolar = sorgu.order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

    # =====================================================
    # ŞUBEYE AİT KURYELER
    # =====================================================

    kuryeler = Kuryeler.query.filter_by(
        sube_id=sube.id
    ).all()

    # =====================================================
    # SAYFAYA GÖNDER
    # =====================================================

    return render_template(
        "personel/sube_personel_kargolar.html",

        kargolar=kargolar,

        sube=sube,

        personel=personel,

        kullanici=personel.kullanici,

        kuryeler=kuryeler,

        takip_no=takip_no,

        gonderici=gonderici,

        alici=alici,

        durum=durum,

        kurye_id=kurye_id,

        tarih=tarih
    )


# =========================================================
# ŞUBE PERSONELİ - KARGO DETAYI
# =========================================================

@main.route("/subepersoneli/kargo/<int:kargo_id>")
def subepersoneli_kargo_detay(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Şube Personeli"):
        return redirect(
            url_for("main.index")
        )

    personel = sube_personelini_getir()

    if not personel:

        flash(
            "Personel bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    if not personel.aktif:

        flash(
            "Personel hesabınız aktif değil."
        )

        return redirect(
            url_for("main.personel_login")
        )

    # =====================================================
    # KARGOYU BUL
    # =====================================================

    kargo = Kargolar.query.filter_by(
        id=kargo_id,
        sube_id=personel.sube_id
    ).first()

    if not kargo:

        flash(
            "Bu kargo bulunamadı veya şubenize ait değil."
        )

        return redirect(
            url_for("main.subepersoneli_kargolar")
        )

    # =====================================================
    # ŞUBE BİLGİSİ
    # =====================================================

    sube = Subeler.query.get(
        personel.sube_id
    )

    # =====================================================
    # KARGO HAREKETLERİ
    # =====================================================

    hareketler = Kargo_Hareketleri.query.filter_by(
        kargo_id=kargo.id
    ).order_by(
        Kargo_Hareketleri.tarih.asc()
    ).all()

    # =====================================================
    # ŞUBEYE AİT KURYELER
    # =====================================================

    kuryeler = Kuryeler.query.filter_by(
        sube_id=personel.sube_id
    ).all()

    # =====================================================
    # DETAY SAYFASI
    # =====================================================

    return render_template(
        "personel/kargo_detay.html",

        kargo=kargo,

        hareketler=hareketler,

        sube=sube,

        personel=personel,

        kullanici=personel.kullanici,

        kuryeler=kuryeler
    )

# =====================================================
# ŞUBE PERSONELİ - KARGO OLUŞTUR
# =====================================================

@main.route(
    "/subepersoneli/kargo/olustur",
    methods=["GET", "POST"]
)
def subepersoneli_kargo_olustur():

    if not giris_kontrolu():
        return redirect(url_for("main.personel_login"))

    if not rol_kontrolu("Şube Personeli"):
        return redirect(url_for("main.index"))

    personel = sube_personelini_getir()

    if not personel or not personel.aktif:
        flash("Personel hesabınız aktif değil.", "danger")
        return redirect(url_for("main.personel_login"))

    sube = Subeler.query.get(personel.sube_id)

    if not sube or not sube.aktif:
        flash("Bağlı olduğunuz şube bulunamadı veya aktif değil.", "danger")
        return redirect(url_for("main.personel_login"))

    # Mevcut HTML yapısını bozmamak için liste tutuluyor; backend yalnızca personelin şubesini kabul eder.
    subeler = [sube]

    musteriler = (
        Kullanicilar.query
        .join(Rol, Kullanicilar.rol_id == Rol.id)
        .filter(Rol.ad == "Müşteri")
        .order_by(Kullanicilar.ad, Kullanicilar.soyad)
        .all()
    )

    kuryeler = Kuryeler.query.filter_by(
        sube_id=personel.sube_id
    ).all()

    kargo_turleri = (
        KargoTurleri.query
        .filter_by(aktif=True)
        .order_by(KargoTurleri.id)
        .all()
    )

    def formu_goster():
        return render_template(
            "personel/kargo_olustur.html",
            sube=sube,
            subeler=subeler,
            musteriler=musteriler,
            personel=personel,
            kullanici=personel.kullanici,
            kuryeler=kuryeler,
            kargo_turleri=kargo_turleri
        )

    if request.method == "POST":

        secilen_sube_id = request.form.get("sube_id", type=int)
        gonderici_id = request.form.get("gonderici_id", type=int)
        alici_id = request.form.get("alici_id", type=int)
        kargo_turu_id = request.form.get("kargo_turu_id", type=int)
        kurye_id = request.form.get("kurye_id", type=int)

        agirlik = request.form.get("agirlik", "").strip()
        desi_en = request.form.get("desi_en", "").strip()
        desi_boy = request.form.get("desi_boy", "").strip()
        desi_yukseklik = request.form.get("desi_yukseklik", "").strip()

        if secilen_sube_id != personel.sube_id:
            flash(
                "Sadece bağlı olduğunuz şube üzerinden kargo oluşturabilirsiniz.",
                "danger"
            )
            return formu_goster()

        gonderici_kullanici = (
            Kullanicilar.query
            .join(Rol, Kullanicilar.rol_id == Rol.id)
            .filter(
                Kullanicilar.id == gonderici_id,
                Rol.ad == "Müşteri"
            )
            .first()
        )

        if not gonderici_kullanici:
            flash("Geçerli bir gönderici seçiniz.", "danger")
            return formu_goster()

        alici_kullanici = (
            Kullanicilar.query
            .join(Rol, Kullanicilar.rol_id == Rol.id)
            .filter(
                Kullanicilar.id == alici_id,
                Rol.ad == "Müşteri"
            )
            .first()
        )

        if not alici_kullanici:
            flash("Geçerli bir alıcı seçiniz.", "danger")
            return formu_goster()

        if gonderici_kullanici.id == alici_kullanici.id:
            flash("Gönderici ve alıcı aynı kişi olamaz.", "danger")
            return formu_goster()

        if not gonderici_kullanici.adres:
            flash("Seçilen göndericinin adres bilgisi bulunmuyor.", "danger")
            return formu_goster()

        # Şube personeli yalnızca kendi şehriyle eşleşen gönderici için işlem yapabilir.
        if not adres_sube_uyumlu_mu(gonderici_kullanici.adres, sube):
            flash(
                "Göndericinin adresi bu şubenin bulunduğu şehirle uyuşmuyor.",
                "danger"
            )
            return formu_goster()

        if not kargo_turu_id:
            flash("Lütfen bir kargo türü seçiniz.", "danger")
            return formu_goster()

        kargo_turu = KargoTurleri.query.filter_by(
            id=kargo_turu_id,
            aktif=True
        ).first()

        if not kargo_turu:
            flash("Seçilen kargo türü bulunamadı.", "danger")
            return formu_goster()

        gonderici = f"{gonderici_kullanici.ad} {gonderici_kullanici.soyad}"
        gonderici_telefon = gonderici_kullanici.telefon or ""
        gonderici_adres = gonderici_kullanici.adres or ""

        if not gonderici_telefon:
            flash("Seçilen göndericinin telefon bilgisi bulunmuyor.", "danger")
            return formu_goster()

        alici = f"{alici_kullanici.ad} {alici_kullanici.soyad}"
        alici_telefon = alici_kullanici.telefon or ""
        alici_adres = alici_kullanici.adres or ""

        if not alici_telefon:
            flash("Seçilen alıcının telefon bilgisi bulunmuyor.", "danger")
            return formu_goster()

        if not alici_adres:
            flash("Seçilen alıcının adres bilgisi bulunmuyor.", "danger")
            return formu_goster()

        try:
            agirlik = float(agirlik)
            if agirlik <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Ağırlık bilgisini doğru giriniz.", "danger")
            return formu_goster()

        try:
            desi_en = float(desi_en)
            desi_boy = float(desi_boy)
            desi_yukseklik = float(desi_yukseklik)

            if desi_en <= 0 or desi_boy <= 0 or desi_yukseklik <= 0:
                raise ValueError

        except (ValueError, TypeError):
            flash(
                "En, boy ve yükseklik bilgilerini doğru giriniz.",
                "danger"
            )
            return formu_goster()

        desi = (desi_en * desi_boy * desi_yukseklik) / 3000

        _, _, _, ucret = kargo_ucreti_hesapla(
            agirlik,
            desi,
            kargo_turu
        )

        if kurye_id:
            kurye = Kuryeler.query.filter_by(
                id=kurye_id,
                sube_id=personel.sube_id
            ).first()

            if not kurye:
                flash("Seçilen kurye bu şubeye ait değil.", "danger")
                return formu_goster()
        else:
            kurye = None

        while True:
            takip_no = f"KRG{random.randint(100000, 999999)}"
            if not Kargolar.query.filter_by(takip_no=takip_no).first():
                break

        kargo = Kargolar(
            takip_no=takip_no,
            gonderici_id=gonderici_kullanici.id,
            gonderici=gonderici,
            gonderici_telefon=gonderici_telefon,
            gonderici_adres=gonderici_adres,
            alici_id=alici_kullanici.id,
            alici=alici,
            alici_telefon=alici_telefon,
            alici_adres=alici_adres,
            kargo_turu_id=kargo_turu.id,
            durum="Hazırlanıyor",
            agirlik=agirlik,
            desi=round(desi, 2),
            ucret=ucret,
            gonderim_tarihi=datetime.now(),
            teslim_tarihi=None,
            sube_id=personel.sube_id,
            kurye_id=kurye.id if kurye else None
        )

        try:
            db.session.add(kargo)
            db.session.flush()

            hareket_aciklama = (
                f"Kargo {sube.sube_ad} şubesinde "
                f"{kargo_turu.ad} gönderi olarak oluşturuldu."
            )

            if kurye:
                hareket_aciklama += (
                    f" {kurye.kullanici.ad} "
                    f"{kurye.kullanici.soyad} isimli kurye atandı."
                )

            hareket = Kargo_Hareketleri(
                kargo_id=kargo.id,
                sube_id=personel.sube_id,
                kurye_id=kurye.id if kurye else None,
                durum="Hazırlanıyor",
                aciklama=hareket_aciklama,
                tarih=datetime.now()
            )

            db.session.add(hareket)
            db.session.commit()

        except Exception:
            db.session.rollback()
            flash("Kargo oluşturulurken bir hata oluştu.", "danger")
            return formu_goster()

        flash(
            f"Kargo başarıyla oluşturuldu. "
            f"Takip numarası: {takip_no} | "
            f"Toplam ücret: {ucret:.2f} ₺",
            "success"
        )

        return redirect(
            url_for(
                "main.subepersoneli_kargo_detay",
                kargo_id=kargo.id
            )
        )

    return formu_goster()

@main.route(
    "/subepersoneli/kargo/<int:kargo_id>/durum-guncelle",
    methods=["POST"]
)
def subepersoneli_kargo_durum_guncelle(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Şube Personeli"):
        return redirect(
            url_for("main.index")
        )

    personel = sube_personelini_getir()

    if not personel:

        flash(
            "Personel bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    if not personel.aktif:

        flash(
            "Personel hesabınız aktif değil."
        )

        return redirect(
            url_for("main.personel_login")
        )

    # -----------------------------------------------------
    # KARGOYU BUL
    # -----------------------------------------------------

    kargo = Kargolar.query.filter_by(
        id=kargo_id,
        sube_id=personel.sube_id
    ).first()

    if not kargo:

        flash(
            "Bu kargo bulunamadı veya şubenize ait değil."
        )

        return redirect(
            url_for("main.subepersoneli_kargolar")
        )

    # -----------------------------------------------------
    # FORM BİLGİLERİ
    # -----------------------------------------------------

    yeni_durum = request.form.get(
        "durum",
        ""
    ).strip()

    aciklama = request.form.get(
        "aciklama",
        ""
    ).strip()

    # -----------------------------------------------------
    # GEÇERLİ DURUMLAR
    # -----------------------------------------------------

    izinli_durumlar = [
        "Hazırlanıyor",
        "Şubede",
        "Dağıtımda",
        "Teslim Edildi",
        "İptal Edildi"
    ]

    if yeni_durum not in izinli_durumlar:

        flash(
            "Geçersiz kargo durumu."
        )

        return redirect(
            url_for(
                "main.subepersoneli_kargo_detay",
                kargo_id=kargo.id
            )
        )

    # -----------------------------------------------------
    # ESKİ DURUM
    # -----------------------------------------------------

    eski_durum = kargo.durum

    # -----------------------------------------------------
    # DURUMU GÜNCELLE
    # -----------------------------------------------------

    kargo.durum = yeni_durum

    if yeni_durum == "Teslim Edildi":

        kargo.teslim_tarihi = datetime.now()

    else:

        kargo.teslim_tarihi = None

    # -----------------------------------------------------
    # AÇIKLAMA
    # -----------------------------------------------------

    if not aciklama:

        if eski_durum == yeni_durum:

            aciklama = (
                "Kargo durumu kontrol edildi."
            )

        else:

            aciklama = (
                f"Kargo durumu {eski_durum} "
                f"durumundan {yeni_durum} "
                f"durumuna güncellendi."
            )

    # -----------------------------------------------------
    # KARGO HAREKETİ OLUŞTUR
    # -----------------------------------------------------

    hareket = Kargo_Hareketleri(

        kargo_id=kargo.id,

        sube_id=personel.sube_id,

        kurye_id=kargo.kurye_id,

        durum=yeni_durum,

        aciklama=aciklama,

        tarih=datetime.now()
    )

    db.session.add(hareket)

    # -----------------------------------------------------
    # VERİTABANINA KAYDET
    # -----------------------------------------------------

    db.session.commit()

    flash(
        f"Kargo durumu '{yeni_durum}' olarak güncellendi."
    )

    # -----------------------------------------------------
    # KARGO DETAYINA DÖN
    # -----------------------------------------------------

    return redirect(
        url_for(
            "main.subepersoneli_kargo_detay",
            kargo_id=kargo.id
        )
    )


# =========================================================
# ŞUBE PERSONELİ - KURYE ATA
# =========================================================

@main.route(
    "/subepersoneli/kargo/<int:kargo_id>/kurye-ata",
    methods=["POST"]
)
def subepersoneli_kurye_ata(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Şube Personeli"):
        return redirect(
            url_for("main.index")
        )

    personel = sube_personelini_getir()

    if not personel or not personel.aktif:

        flash(
            "Personel hesabınız aktif değil."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargo = Kargolar.query.filter_by(
        id=kargo_id,
        sube_id=personel.sube_id
    ).first()

    if not kargo:

        flash(
            "Bu kargo bulunamadı veya şubenize ait değil."
        )

        return redirect(
            url_for("main.subepersoneli_panel")
        )

    kurye_id = request.form.get(
        "kurye_id",
        type=int
    )

    # -------------------------------------------------
    # KURYE ATAMASINI KALDIR
    # -------------------------------------------------

    if kurye_id == 0:

        if kargo.kurye_id is not None:

            eski_kurye = kargo.kurye

            eski_kurye_adi = (
                f"{eski_kurye.kullanici.ad} "
                f"{eski_kurye.kullanici.soyad}"
            )

            kargo.kurye_id = None

            hareket = Kargo_Hareketleri(

                kargo_id=kargo.id,

                sube_id=personel.sube_id,

                kurye_id=None,

                durum=kargo.durum,

                aciklama=(
                    f"Kargo {eski_kurye_adi} "
                    f"isimli kuryeden alındı."
                ),

                tarih=datetime.now()
            )

            db.session.add(hareket)

            db.session.commit()

            flash(
                "Kurye ataması kaldırıldı."
            )

        else:

            flash(
                "Bu kargoya atanmış bir kurye bulunmuyor."
            )

        return redirect(
            url_for(
                "main.subepersoneli_kargo_detay",
                kargo_id=kargo.id
            )
        )

    # -------------------------------------------------
    # KURYE SEÇİMİ
    # -------------------------------------------------

    if not kurye_id:

        flash(
            "Lütfen bir kurye seçiniz."
        )

        return redirect(
            url_for(
                "main.subepersoneli_kargo_detay",
                kargo_id=kargo.id
            )
        )

    # -------------------------------------------------
    # KURYENİN ŞUBEYE AİT OLDUĞUNU KONTROL ET
    # -------------------------------------------------

    kurye = Kuryeler.query.filter_by(
        id=kurye_id,
        sube_id=personel.sube_id
    ).first()

    if not kurye:

        flash(
            "Seçilen kurye bu şubeye ait değil."
        )

        return redirect(
            url_for(
                "main.subepersoneli_kargo_detay",
                kargo_id=kargo.id
            )
        )

    # -------------------------------------------------
    # KURYEYİ ATA
    # -------------------------------------------------

    kargo.kurye_id = kurye.id

    hareket = Kargo_Hareketleri(

        kargo_id=kargo.id,

        sube_id=personel.sube_id,

        kurye_id=kurye.id,

        durum=kargo.durum,

        aciklama=(
            f"Kargo {kurye.kullanici.ad} "
            f"{kurye.kullanici.soyad} "
            f"isimli kuryeye atandı."
        ),

        tarih=datetime.now()
    )

    db.session.add(hareket)

    # -------------------------------------------------
    # KURYEE BİLDİRİM GÖNDER
    # -------------------------------------------------

    bildirim_olustur(

        kullanici_id=kurye.kullanici_id,

        baslik="Yeni Kargo Ataması",

        mesaj=(
            f"{kargo.takip_no} takip numaralı kargo "
            f"size atanmıştır."
        ),

        kargo_id=kargo.id
    )

    db.session.commit()

    flash(
        "Kurye başarıyla atandı."
    )

    return redirect(
        url_for(
            "main.subepersoneli_kargo_detay",
            kargo_id=kargo.id
        )
    )
# =========================================================
# KURYE PANELİ
# =========================================================

@main.route("/kurye_panel")
def kurye_panel():

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Kurye"):
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    kurye = kuryeyi_getir()

    if not kullanici or not kurye:

        flash(
            "Kurye bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargolar = Kargolar.query.filter_by(
        kurye_id=kurye.id
    ).order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

    return render_template(
        "panel/kurye_panel.html",

        kurye=kurye,

        kullanici=kullanici,

        sube=kurye.sube,

        kargolar=kargolar,

        toplam_kargo=len(kargolar),

        bekleyen_kargo=Kargolar.query.filter(
            Kargolar.kurye_id == kurye.id,
            Kargolar.durum != "Teslim Edildi"
        ).count(),

        teslim_edilen_kargo=Kargolar.query.filter_by(
            kurye_id=kurye.id,
            durum="Teslim Edildi"
        ).count()
    )


# =========================================================
# KURYE - KARGOLARIM
# =========================================================

@main.route("/kurye/kargolarim")
def kurye_kargolarim():

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Kurye"):
        return redirect(
            url_for("main.index")
        )

    kurye = kuryeyi_getir()

    if not kurye:

        flash(
            "Kurye bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargolar = Kargolar.query.filter_by(
        kurye_id=kurye.id
    ).order_by(
        Kargolar.gonderim_tarihi.desc()
    ).all()

    return render_template(
        "kurye/kargolarim.html",

        kurye=kurye,

        kullanici=kurye.kullanici,

        sube=kurye.sube,

        kargolar=kargolar
    )


# =========================================================
# KURYE - KARGO DETAYI
# =========================================================

@main.route("/kurye/kargo/<int:kargo_id>")
def kurye_kargo_detay(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Kurye"):
        return redirect(
            url_for("main.index")
        )

    kurye = kuryeyi_getir()

    if not kurye:

        flash(
            "Kurye bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargo = Kargolar.query.filter_by(
        id=kargo_id,
        kurye_id=kurye.id
    ).first()

    if not kargo:

        flash(
            "Bu kargo size atanmamış veya bulunamadı."
        )

        return redirect(
            url_for("main.kurye_kargolarim")
        )

    return render_template(
        "kurye/kargo_detay.html",

        kargo=kargo,

        hareketler=kargo_hareketlerini_getir(
            kargo.id
        ),

        kurye=kurye,

        kullanici=kurye.kullanici,

        sube=kurye.sube
    )
# =========================================================
# KURYE - PERFORMANSIM
# =========================================================

@main.route("/kurye/performansim")
def kurye_performansim():

    # -----------------------------------------------------
    # GİRİŞ / ROL KONTROLÜ
    # -----------------------------------------------------

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Kurye"):
        return redirect(
            url_for("main.index")
        )

    # -----------------------------------------------------
    # KURYE
    # -----------------------------------------------------

    kurye = kuryeyi_getir()

    if not kurye:
        flash(
            "Kurye bilgileri bulunamadı.",
            "danger"
        )

        return redirect(
            url_for("main.personel_login")
        )

    # -----------------------------------------------------
    # KURYENİN KARGOLARI
    # -----------------------------------------------------

    kargolar = (
        Kargolar.query
        .filter_by(
            kurye_id=kurye.id
        )
        .all()
    )

    toplam_kargo = len(kargolar)

    teslim_edilen = sum(
        1
        for kargo in kargolar
        if kargo.durum == "Teslim Edildi"
    )

    dagitimda = sum(
        1
        for kargo in kargolar
        if kargo.durum == "Dağıtımda"
    )

    bekleyen = sum(
        1
        for kargo in kargolar
        if kargo.durum not in [
            "Teslim Edildi",
            "İptal Edildi"
        ]
    )

    # -----------------------------------------------------
    # TESLİMAT ORANI
    # -----------------------------------------------------

    if toplam_kargo > 0:
        teslimat_orani = round(
            (
                teslim_edilen /
                toplam_kargo
            ) * 100,
            1
        )
    else:
        teslimat_orani = 0

    # -----------------------------------------------------
    # ORTALAMA TESLİMAT SÜRESİ
    # -----------------------------------------------------

    teslim_sureleri = []

    for kargo in kargolar:

        if (
            kargo.durum == "Teslim Edildi"
            and kargo.gonderim_tarihi
            and kargo.teslim_tarihi
        ):

            fark = (
                kargo.teslim_tarihi -
                kargo.gonderim_tarihi
            )

            teslim_sureleri.append(
                fark.total_seconds()
            )

    if teslim_sureleri:

        ortalama_saniye = (
            sum(teslim_sureleri) /
            len(teslim_sureleri)
        )

        ortalama_saat = round(
            ortalama_saniye / 3600,
            1
        )

    else:

        ortalama_saat = 0

    # -----------------------------------------------------
    # MÜŞTERİ DEĞERLENDİRMELERİ
    # -----------------------------------------------------

    degerlendirme_kayitlari = (
        db.session.query(
            Degerlendirmeler,
            Kargolar
        )
        .join(
            Kargolar,
            Degerlendirmeler.kargo_id == Kargolar.id
        )
        .filter(
            Kargolar.kurye_id == kurye.id
        )
        .order_by(
            Degerlendirmeler.tarih.desc()
        )
        .all()
    )

    degerlendirme_sayisi = len(
        degerlendirme_kayitlari
    )

    if degerlendirme_sayisi > 0:

        ortalama_puan = round(
            sum(
                degerlendirme.puan
                for degerlendirme, _ in degerlendirme_kayitlari
            ) / degerlendirme_sayisi,
            1
        )

    else:

        ortalama_puan = 0

    puan_dagilimi = {
        5: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 0
    }

    for degerlendirme, _ in degerlendirme_kayitlari:

        if degerlendirme.puan in puan_dagilimi:

            puan_dagilimi[
                degerlendirme.puan
            ] += 1

    # Müşteri kimliğini göstermeden son yorumlar
    son_degerlendirmeler = []

    for degerlendirme, _ in degerlendirme_kayitlari[:6]:

        son_degerlendirmeler.append({
            "puan": degerlendirme.puan,
            "yorum": degerlendirme.yorum,
            "tarih": degerlendirme.tarih
        })

    # -----------------------------------------------------
    # SAYFAYI GÖSTER
    # -----------------------------------------------------

    return render_template(
        "kurye/performansim.html",

        kurye=kurye,
        kullanici=kurye.kullanici,
        sube=kurye.sube,

        toplam_kargo=toplam_kargo,
        teslim_edilen=teslim_edilen,
        dagitimda=dagitimda,
        bekleyen=bekleyen,

        teslimat_orani=teslimat_orani,
        ortalama_saat=ortalama_saat,

        ortalama_puan=ortalama_puan,
        degerlendirme_sayisi=degerlendirme_sayisi,
        puan_dagilimi=puan_dagilimi,
        son_degerlendirmeler=son_degerlendirmeler
    )


# =========================================================
# KURYE - TESLİMATA ÇIKAR
# =========================================================

@main.route(
    "/kurye/kargo/<int:kargo_id>/teslimata-cikar",
    methods=["POST"]
)
def kurye_teslimata_cikar(kargo_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.personel_login")
        )

    if not rol_kontrolu("Kurye"):
        return redirect(
            url_for("main.index")
        )

    kurye = kuryeyi_getir()

    if not kurye:

        flash(
            "Kurye bilgileri bulunamadı."
        )

        return redirect(
            url_for("main.personel_login")
        )

    kargo = Kargolar.query.filter_by(
        id=kargo_id,
        kurye_id=kurye.id
    ).first()

    if not kargo:

        flash(
            "Bu kargo size atanmamış veya bulunamadı."
        )

        return redirect(
            url_for("main.kurye_kargolarim")
        )

    if kargo.durum == "Teslim Edildi":

        flash(
            "Bu kargo zaten teslim edilmiş."
        )

        return redirect(
            url_for(
                "main.kurye_kargo_detay",
                kargo_id=kargo.id
            )
        )

    if kargo.durum == "İptal Edildi":

        flash(
            "İptal edilmiş kargo teslimata çıkarılamaz."
        )

        return redirect(
            url_for(
                "main.kurye_kargo_detay",
                kargo_id=kargo.id
            )
        )

    kargo.durum = "Dağıtımda"

    hareket = Kargo_Hareketleri(

        kargo_id=kargo.id,

        sube_id=kargo.sube_id,

        kurye_id=kurye.id,

        durum="Dağıtımda",

        aciklama=(
            f"Kargo {kurye.kullanici.ad} "
            f"{kurye.kullanici.soyad} "
            f"isimli kurye tarafından teslimata çıkarıldı."
        ),

        tarih=datetime.now()
    )

    db.session.add(hareket)

    db.session.commit()

    flash(
        "Kargo başarıyla teslimata çıkarıldı."
    )

    return redirect(
        url_for("main.kurye_kargo_detay",kargo_id=kargo.id))

# KURYE - TESLİM EDİLDİ

@main.route(
    "/kurye/kargo/<int:kargo_id>/teslim-edildi",
    methods=["POST"]
)
def kurye_teslim_edildi(kargo_id):

    if not giris_kontrolu():
        return redirect(url_for("main.personel_login"))

    if not rol_kontrolu("Kurye"):
        return redirect(url_for("main.index"))

    kurye = kuryeyi_getir()

    if not kurye:

        flash("Kurye bilgileri bulunamadı.")

        return redirect(url_for("main.personel_login"))

    kargo = Kargolar.query.filter_by(id=kargo_id,kurye_id=kurye.id).first()

    if not kargo:

        flash("Bu kargo size atanmamış veya bulunamadı.")

        return redirect(url_for("main.kurye_kargolarim"))

    if kargo.durum == "Teslim Edildi":

        flash("Bu kargo zaten teslim edilmiş.")

        return redirect(
            url_for("main.kurye_kargo_detay",kargo_id=kargo.id))

    if kargo.durum == "İptal Edildi":

        flash("İptal edilmiş kargo teslim edilemez.")

        return redirect(
            url_for("main.kurye_kargo_detay",kargo_id=kargo.id))

    kargo.durum = "Teslim Edildi"

    kargo.teslim_tarihi = datetime.now()

    hareket = Kargo_Hareketleri(

        kargo_id=kargo.id,

        sube_id=kargo.sube_id,

        kurye_id=kurye.id,

        durum="Teslim Edildi",

        aciklama=(
            f"Kargo {kurye.kullanici.ad} "
            f"{kurye.kullanici.soyad} "
            f"isimli kurye tarafından teslim edildi."
        ),

        tarih=datetime.now()
    )

    db.session.add(hareket)

    db.session.commit()

    flash("Kargo teslim edildi olarak işaretlendi.")

    return redirect(url_for("main.kurye_kargo_detay",kargo_id=kargo.id))
# =========================================================
# KULLANICI - PROFİLİM
# =========================================================

@main.route("/profilim")
def profilim():

    if not giris_kontrolu():
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    if not kullanici:
        return redirect(
            url_for("main.index")
        )

    return render_template(
        "profilim.html",
        kullanici=kullanici
    )


# =========================================================
# KULLANICI - PROFİL DÜZENLE
# =========================================================

@main.route(
    "/profilim/duzenle",
    methods=["GET", "POST"]
)
def profil_duzenle():

    if not giris_kontrolu():
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    if not kullanici:
        return redirect(
            url_for("main.index")
        )

    if request.method == "POST":

        ad = request.form.get(
            "ad",
            ""
        ).strip()

        soyad = request.form.get(
            "soyad",
            ""
        ).strip()

        telefon = request.form.get(
            "telefon",
            ""
        ).strip()

        adres = request.form.get(
            "adres",
            ""
        ).strip()

        if not ad or not soyad:

            flash(
                "Ad ve soyad alanları boş bırakılamaz.",
                "danger"
            )

            return render_template(
                "profil_duzenle.html",
                kullanici=kullanici
            )

        kullanici.ad = ad
        kullanici.soyad = soyad
        kullanici.telefon = telefon
        kullanici.adres = adres

        db.session.commit()

        flash(
            "Profil bilgileriniz başarıyla güncellendi.",
            "success"
        )

        return redirect(
            url_for("main.profilim")
        )

    return render_template(
        "profil_duzenle.html",
        kullanici=kullanici
    )
# =========================================================
# KULLANICI - BİLDİRİMLER
# =========================================================

@main.route("/bildirimler")
def bildirimler():

    if not giris_kontrolu():
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    if not kullanici:
        return redirect(
            url_for("main.index")
        )

    bildirimler = Bildirimler.query.filter_by(
        kullanici_id=kullanici.id
    ).order_by(
        Bildirimler.tarih.desc()
    ).all()

    okunmamis_sayi = Bildirimler.query.filter_by(
        kullanici_id=kullanici.id,
        okundu=False
    ).count()

    return render_template(
        "bildirimler.html",
        kullanici=kullanici,
        bildirimler=bildirimler,
        okunmamis_sayi=okunmamis_sayi
    )


# =========================================================
# BİLDİRİM - OKUNDU OLARAK İŞARETLE
# =========================================================

@main.route(
    "/bildirimler/okundu/<int:bildirim_id>",
    methods=["POST"]
)
def bildirim_okundu(bildirim_id):

    if not giris_kontrolu():
        return redirect(
            url_for("main.index")
        )

    kullanici = mevcut_kullanici()

    if not kullanici:
        return redirect(
            url_for("main.index")
        )

    bildirim = Bildirimler.query.filter_by(
        id=bildirim_id,
        kullanici_id=kullanici.id
    ).first()

    if bildirim:

        bildirim.okundu = True

        db.session.commit()

    return redirect(
        url_for("main.bildirimler")
    )
@main.app_context_processor
def bildirim_sayisi():

    kullanici_id = session.get("kullanici_id")

    if not kullanici_id:
        return {
            "okunmamis_bildirim_sayisi": 0
        }

    sayi = Bildirimler.query.filter_by(
        kullanici_id=kullanici_id,
        okundu=False
    ).count()

    return {
        "okunmamis_bildirim_sayisi": sayi
    }
# =========================================================
# HAKKIMIZDA
# =========================================================

@main.route("/hakkimizda")
def hakkimizda():
    return render_template(
        "hakkimizda.html"
    )


# =========================================================
# HİZMETLERİMİZ
# =========================================================

@main.route("/hizmetlerimiz")
def hizmetlerimiz():
    return render_template(
        "hizmetlerimiz.html"
    )


# =========================================================
# İLETİŞİM
# =========================================================

@main.route("/iletisim")
def iletisim():
    return render_template(
        "iletisim.html"
    )
# ÇIKIŞ

@main.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("main.index"))