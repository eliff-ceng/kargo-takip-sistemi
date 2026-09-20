from app import create_app, db

uygulama = create_app()

with uygulama.app_context():

    print("Tablolar siliniyor...")

    db.drop_all()

    print("Tüm tablolar başarıyla silindi.")

    db.create_all()

    print("Tablolar yeniden oluşturuldu.")