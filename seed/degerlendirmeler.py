from app import create_app, db
from app.models import (
    Degerlendirmeler,
    Kargolar,
    Kullanicilar
)
from datetime import datetime, timedelta


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
    # ESKİ TEST DEĞERLENDİRMELERİNİ SİL
    # ============================================================

    test_takip_nolari = [
        f"KRG{i:06d}"
        for i in range(1, 21)
    ]

    test_kargolari = Kargolar.query.filter(
        Kargolar.takip_no.in_(test_takip_nolari)
    ).all()

    test_kargo_idleri = [
        kargo.id
        for kargo in test_kargolari
    ]

    if test_kargo_idleri:

        Degerlendirmeler.query.filter(
            Degerlendirmeler.kargo_id.in_(test_kargo_idleri)
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

        print("Eski test değerlendirmeleri silindi.")


    # ============================================================
    # DEĞERLENDİRME OLUŞTURMA FONKSİYONU
    # ============================================================

    def degerlendirme_olustur(
        takip_no,
        kullanici_adi,
        puan,
        yorum,
        gun
    ):

        kargo = Kargolar.query.filter_by(
            takip_no=takip_no
        ).first()

        kullanici = kullanicilar[kullanici_adi]

        return Degerlendirmeler(
            kargo_id=kargo.id,
            kullanici_id=kullanici.id,
            puan=puan,
            yorum=yorum,
            tarih=datetime.now() - timedelta(days=gun)
        )


    # ============================================================
    # DEĞERLENDİRMELER
    #
    # Sadece TESLİM EDİLDİ durumundaki kargolar
    # değerlendiriliyor.
    # ============================================================

    degerlendirmeler = [

        degerlendirme_olustur("KRG100001", "mustafayalcin", 5, "Kargom zamanında ve sorunsuz şekilde teslim edildi.", 1),

        degerlendirme_olustur("KRG100006", "canancandan", 4, "Teslimat hızlıydı, kargom sağlam ulaştı.", 2),

        degerlendirme_olustur("KRG100010", "ziyayazici", 5, "Kargo beklediğimden daha hızlı teslim edildi.", 2),

        degerlendirme_olustur("KRG100012", "aysegulyilmaz", 5, "Herhangi bir sorun yaşamadım, teşekkür ederim.", 3),

        degerlendirme_olustur("KRG100014", "fikrettekin", 4, "Teslimat başarılıydı, kargom sağlam geldi.", 3),

        degerlendirme_olustur("KRG100018", "sinemacar", 5, "Kargom sorunsuz bir şekilde teslim edildi.", 2),

        degerlendirme_olustur("KRG100020", "buraksezer", 4, "Genel olarak memnun kaldım.", 1)

    ]


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(degerlendirmeler)
    db.session.commit()

    print(f"{len(degerlendirmeler)} değerlendirme başarıyla eklendi.")