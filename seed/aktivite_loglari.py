from app import create_app, db
from app.models import (
    AktiviteLoglari,
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
    # TEST KARGOLARINI BUL
    # KRG100001 - KRG100020
    # ============================================================

    takip_nolari = [
        f"KRG{100000 + i}"
        for i in range(1, 21)
    ]

    kargolar = {
        k.takip_no: k
        for k in Kargolar.query.filter(
            Kargolar.takip_no.in_(takip_nolari)
        ).all()
    }


    # ============================================================
    # ESKİ TEST AKTİVİTELERİNİ SİL
    # Sadece bu 20 kargoya ait aktiviteler silinir.
    # Diğer aktivitelere dokunulmaz.
    # ============================================================

    kargo_idleri = [
        kargo.id
        for kargo in kargolar.values()
    ]

    if kargo_idleri:

        AktiviteLoglari.query.filter(
            AktiviteLoglari.kargo_id.in_(kargo_idleri)
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

        print("Eski test aktivite kayıtları silindi.")


    # ============================================================
    # AKTİVİTE OLUŞTURMA FONKSİYONU
    # ============================================================

    def aktivite_olustur(kullanici_id, kargo_id, islem, aciklama, gun=0):

        return AktiviteLoglari(
            kullanici_id=kullanici_id,
            kargo_id=kargo_id,
            islem=islem,
            aciklama=aciklama,
            tarih=datetime.now() - timedelta(days=gun)
        )


    # ============================================================
    # AKTİVİTELER
    # ============================================================

    aktiviteler = []


    # ============================================================
    # 1 - KRG100001
    # Isparta -> Konya
    # ============================================================

    kargo = kargolar["KRG100001"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo bilgileri", f"{kargo.takip_no} kargosunun gönderici ve alıcı bilgileri sisteme kaydedildi.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kurye atama", f"{kargo.takip_no} kargosuna kurye ataması yapıldı.", 4))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Durum güncelleme", f"{kargo.takip_no} kargosunun durumu Dağıtımda olarak güncellendi.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 2))


    # ============================================================
    # 2 - KRG100002
    # Konya -> Ankara
    # ============================================================

    kargo = kargolar["KRG100002"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosunun çıkış şubesine kabul işlemi yapıldı.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Ankara yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kurye atama", f"{kargo.takip_no} kargosuna Ankara şubesindeki kurye ataması yapıldı.", 0))


    # ============================================================
    # 3 - KRG100003
    # Ankara -> İstanbul
    # ============================================================

    kargo = kargolar["KRG100003"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosunun Ankara Çankaya şubesine kabul işlemi yapıldı.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu İstanbul yönüne sevk edildi.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo durumu", f"{kargo.takip_no} kargosunun durumu Yolda olarak güncellendi.", 1))


    # ============================================================
    # 4 - KRG100004
    # İstanbul -> İzmir
    # ============================================================

    kargo = kargolar["KRG100004"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu İzmir yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu İzmir Konak şubesine ulaştı.", 0))


    # ============================================================
    # 5 - KRG100005
    # İzmir -> Bursa
    # ============================================================

    kargo = kargolar["KRG100005"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 4))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Bursa yönüne sevk edildi.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Bursa Osmangazi şubesine ulaştı.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Bursa Osmangazi bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 6 - KRG100006
    # Bursa -> İstanbul
    # ============================================================

    kargo = kargolar["KRG100006"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 7))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu İstanbul yönüne sevk edildi.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu İstanbul Kadıköy şubesine ulaştı.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 4))


    # ============================================================
    # 7 - KRG100007
    # İstanbul -> Adana
    # ============================================================

    kargo = kargolar["KRG100007"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Adana yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Adana Seyhan bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 8 - KRG100008
    # Adana -> Eskişehir
    # ============================================================

    kargo = kargolar["KRG100008"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Eskişehir yönüne sevk edildi.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo durumu", f"{kargo.takip_no} kargosunun durumu Yolda olarak güncellendi.", 1))


    # ============================================================
    # 9 - KRG100009
    # Eskişehir -> Ankara
    # ============================================================

    kargo = kargolar["KRG100009"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Ankara yönüne sevk edildi.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Ankara Çankaya şubesine ulaştı.", 0))


    # ============================================================
    # 10 - KRG100010
    # Ankara -> Kayseri
    # ============================================================

    kargo = kargolar["KRG100010"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Kayseri yönüne sevk edildi.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Kayseri Melikgazi bölgesinde dağıtıma çıkarıldı.", 4))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 3))


    # ============================================================
    # 11 - KRG100011
    # Kayseri -> Samsun
    # ============================================================

    kargo = kargolar["KRG100011"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Samsun yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Samsun Atakum şubesine ulaştı.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Samsun Atakum bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 12 - KRG100012
    # Samsun -> Isparta
    # ============================================================

    kargo = kargolar["KRG100012"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 7))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Isparta yönüne sevk edildi.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Isparta Merkez şubesine ulaştı.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Isparta Merkez bölgesinde dağıtıma çıkarıldı.", 4))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 4))


    # ============================================================
    # 13 - KRG100013
    # Isparta -> Antalya
    # ============================================================

    kargo = kargolar["KRG100013"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Antalya yönüne sevk edildi.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Antalya Kepez bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 14 - KRG100014
    # Antalya -> Konya
    # ============================================================

    kargo = kargolar["KRG100014"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 8))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Konya yönüne sevk edildi.", 7))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Konya Selçuklu şubesine ulaştı.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Konya Selçuklu bölgesinde dağıtıma çıkarıldı.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 5))


    # ============================================================
    # 15 - KRG100015
    # Konya -> Eskişehir
    # ============================================================

    kargo = kargolar["KRG100015"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Eskişehir yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Eskişehir Odunpazarı şubesine ulaştı.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Eskişehir Odunpazarı bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 16 - KRG100016
    # Eskişehir -> Bursa
    # ============================================================

    kargo = kargolar["KRG100016"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo hazırlama", f"{kargo.takip_no} kargosunun gönderim hazırlıkları başlatıldı.", 0))


    # ============================================================
    # 17 - KRG100017
    # Bursa -> Antalya
    # ============================================================

    kargo = kargolar["KRG100017"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Antalya yönüne sevk edildi.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Antalya Kepez şubesine ulaştı.", 0))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Antalya Kepez bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 18 - KRG100018
    # Antalya -> Isparta
    # ============================================================

    kargo = kargolar["KRG100018"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 7))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Isparta yönüne sevk edildi.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Isparta Merkez şubesine ulaştı.", 5))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Isparta Merkez bölgesinde dağıtıma çıkarıldı.", 4))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 4))


    # ============================================================
    # 19 - KRG100019
    # Isparta Davraz -> Antalya Merkez
    # ============================================================

    kargo = kargolar["KRG100019"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 3))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu Antalya yönüne sevk edildi.", 2))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu Antalya Merkez şubesine ulaştı.", 1))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu Antalya Merkez bölgesinde dağıtıma çıkarıldı.", 0))


    # ============================================================
    # 20 - KRG100020
    # İstanbul Beşiktaş -> İzmir Bornova
    # ============================================================

    kargo = kargolar["KRG100020"]

    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo oluşturma", f"{kargo.takip_no} takip numaralı kargo oluşturuldu.", 9))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Kargo sevki", f"{kargo.takip_no} kargosu İzmir yönüne sevk edildi.", 8))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Şubeye kabul", f"{kargo.takip_no} kargosu İzmir Bornova şubesine ulaştı.", 7))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Dağıtım", f"{kargo.takip_no} kargosu İzmir bölgesinde dağıtıma çıkarıldı.", 6))
    aktiviteler.append(aktivite_olustur(kargo.gonderici_id, kargo.id, "Teslimat", f"{kargo.takip_no} kargosunun teslim edildiği kaydedildi.", 6))


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(aktiviteler)
    db.session.commit()

    print(f"{len(aktiviteler)} aktivite başarıyla eklendi.")