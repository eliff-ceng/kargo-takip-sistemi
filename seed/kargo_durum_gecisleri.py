from app import create_app, db
from app.models import KargoDurumGecisleri


uygulama = create_app()


with uygulama.app_context():

    # ============================================================
    # ESKİ DURUM GEÇİŞLERİNİ TEMİZLE
    # ============================================================

    KargoDurumGecisleri.query.delete()
    db.session.commit()

    print("Eski kargo durum geçişleri temizlendi.")


    # ============================================================
    # KARGO DURUM GEÇİŞLERİ
    #
    # Hazırlanıyor → Şubede → Yolda → Dağıtımda → Teslim Edildi
    #
    # Teslim Edildi son durumdur.
    # ============================================================

    durum_gecisleri = [

        KargoDurumGecisleri(mevcut_durum="Hazırlanıyor", sonraki_durum="Şubede", aktif=True),

        KargoDurumGecisleri(mevcut_durum="Şubede", sonraki_durum="Yolda", aktif=True),

        KargoDurumGecisleri(mevcut_durum="Yolda", sonraki_durum="Şubede", aktif=True),

        KargoDurumGecisleri(mevcut_durum="Yolda", sonraki_durum="Dağıtımda", aktif=True),

        KargoDurumGecisleri(mevcut_durum="Dağıtımda", sonraki_durum="Teslim Edildi", aktif=True)

    ]


    # ============================================================
    # VERİTABANINA EKLE
    # ============================================================

    db.session.add_all(durum_gecisleri)
    db.session.commit()

    print(f"{len(durum_gecisleri)} kargo durum geçişi başarıyla eklendi.")