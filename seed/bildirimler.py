from app import create_app, db
from app.models import (
    Bildirimler,
    Kargolar
)
from datetime import datetime


uygulama = create_app()


with uygulama.app_context():

    # ============================================================
    # TEST KARGOLARINI BUL
    # KRG100001 - KRG100020
    # ============================================================

    takip_nolari = [
        f"KRG{100000 + i}"
        for i in range(1, 21)
    ]

    kargolar = Kargolar.query.filter(
        Kargolar.takip_no.in_(takip_nolari)
    ).all()


    # ============================================================
    # BİLDİRİM OLUŞTURMA FONKSİYONU
    # ============================================================

    def bildirim_olustur(kullanici_id, kargo_id, baslik, mesaj, okundu=False):

        return Bildirimler(
            kullanici_id=kullanici_id,
            kargo_id=kargo_id,
            baslik=baslik,
            mesaj=mesaj,
            okundu=okundu,
            tarih=datetime.now()
        )


    # ============================================================
    # BİLDİRİMLER
    # ============================================================

    bildirimler = []


    for kargo in kargolar:

        # ========================================================
        # GÖNDERİCİ BİLDİRİMİ
        # ========================================================

        if kargo.gonderici_id:

            if kargo.durum == "Teslim Edildi":

                bildirimler.append(bildirim_olustur(kargo.gonderici_id, kargo.id, "Kargonuz teslim edildi", f"{kargo.takip_no} takip numaralı kargonuz alıcısına başarıyla teslim edildi."))

            elif kargo.durum == "Dağıtımda":

                bildirimler.append(bildirim_olustur(kargo.gonderici_id, kargo.id, "Kargonuz dağıtımda", f"{kargo.takip_no} takip numaralı kargonuz dağıtıma çıkarıldı."))

            elif kargo.durum == "Yolda":

                bildirimler.append(bildirim_olustur(kargo.gonderici_id, kargo.id, "Kargonuz yolda", f"{kargo.takip_no} takip numaralı kargonuz varış şubesine doğru yola çıktı."))

            elif kargo.durum == "Şubede":

                bildirimler.append(bildirim_olustur(kargo.gonderici_id, kargo.id, "Kargonuz şubede", f"{kargo.takip_no} takip numaralı kargonuz şubeye ulaştı."))

            else:

                bildirimler.append(bildirim_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturuldu", f"{kargo.takip_no} takip numaralı kargonuz sisteme kaydedildi."))


        # ========================================================
        # ALICI BİLDİRİMİ
        # ========================================================

        if kargo.alici_id:

            if kargo.durum == "Teslim Edildi":

                bildirimler.append(bildirim_olustur(kargo.alici_id, kargo.id, "Kargonuz teslim edildi", f"{kargo.takip_no} takip numaralı kargonuz tarafınıza teslim edildi."))

            elif kargo.durum == "Dağıtımda":

                bildirimler.append(bildirim_olustur(kargo.alici_id, kargo.id, "Kargonuz dağıtımda", f"{kargo.takip_no} takip numaralı kargonuz bulunduğunuz bölgedeki kurye tarafından dağıtıma çıkarıldı."))

            elif kargo.durum == "Yolda":

                bildirimler.append(bildirim_olustur(kargo.alici_id, kargo.id, "Kargonuz yolda", f"{kargo.takip_no} takip numaralı kargonuz varış şubesine doğru ilerliyor."))

            elif kargo.durum == "Şubede":

                bildirimler.append(bildirim_olustur(kargo.alici_id, kargo.id, "Kargonuz şubeye ulaştı", f"{kargo.takip_no} takip numaralı kargonuz varış şubesine ulaştı."))

            else:

                bildirimler.append(bildirim_olustur(kargo.alici_id, kargo.id, "Yeni kargo", f"{kargo.takip_no} takip numaralı kargo adınıza gönderildi."))


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(bildirimler)
    db.session.commit()

    print(f"{len(bildirimler)} bildirim başarıyla eklendi.")