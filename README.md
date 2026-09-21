Kargo Takip Sistemi
Proje Hakkında

Kargo Takip Sistemi, kargo gönderim ve teslimat süreçlerinin dijital ortamda yönetilmesini ve takip edilmesini sağlayan web tabanlı bir uygulamadır.
Proje; müşterilerin kargo oluşturabilmesi ve gönderilerinin durumunu takip edebilmesi, şube personelinin kargo operasyonlarını yönetebilmesi, kuryelerin kendilerine atanan gönderileri takip edebilmesi ve yöneticilerin sistem genelindeki operasyonları merkezi olarak yönetebilmesi amacıyla geliştirilmiştir.
Uygulama, farklı kullanıcı rollerinin yetkilerinin birbirinden ayrıldığı rol bazlı bir yapı üzerine kurulmuştur. Kargo oluşturma işleminden teslimat sürecine kadar gerçekleşen işlemler kayıt altına alınarak kargo hareketlerinin izlenebilir olması sağlanmaktadır.

Temel Özellikler
Kullanıcı kayıt ve giriş sistemi
Rol bazlı yetkilendirme
Kargo oluşturma ve takip
Takip numarası ile kargo sorgulama
Kargo durum ve hareket geçmişi
Şube ve kurye yönetimi
Kullanıcı profil ve profil fotoğrafı yönetimi
Kargo ağırlık ve desi hesaplama
Dinamik kargo ücretlendirme
Kargo türü yönetimi
Kargo arama ve filtreleme
Kargo durum bildirimleri
Müşteri değerlendirme sistemi
Yönetim paneli
İstatistik ve grafik tabanlı raporlama
Kurye performans takibi
Kullanıcı Rolleri

Sistem, farklı kullanıcı gruplarının görev ve yetkilerine göre dört temel rol içermektedir.

Rol	Temel İşlevler
Yönetici	Kullanıcı, kargo, şube ve kurye yönetimi; sistem istatistiklerinin takibi
Şube Personeli	Kargo oluşturma, düzenleme, kurye atama ve kargo durum yönetimi
Kurye	Kendisine atanan kargoların teslimat süreçlerinin yönetimi
Müşteri	Kargo oluşturma, kargo takibi ve değerlendirme işlemleri
Kargo Yönetimi

Sistem üzerinden kargo oluşturma, takip etme ve teslimat sürecinin yönetilmesi sağlanmaktadır.

Kargo oluşturulurken gönderici ve alıcı bilgileri, kargo türü, ağırlık, boyut ve teslimat bilgileri sisteme kaydedilmektedir.

Her kargo için benzersiz bir takip numarası oluşturulmakta ve kargonun süreç içerisindeki durum değişiklikleri kargo hareketleri üzerinden kayıt altına alınmaktadır.

Kargo durumları:

Hazırlanıyor
Şubede
Dağıtımda
Teslim Edildi
İptal Edildi
Fiyatlandırma

Kargo ücretlendirme sistemi, gönderinin ağırlık ve desi değerleri dikkate alınarak çalışmaktadır.

Desi hesaplama:

Desi = (En × Boy × Yükseklik) / 3000

Hesaplama sonucunda ağırlık ve desi değerlerinden uygun olan değer esas alınarak kademeli fiyatlandırma uygulanmaktadır.

Sistemde ayrıca kullanıcıların gönderi bilgilerini girerek tahmini kargo ücretini hesaplayabildiği ayrı bir fiyat hesaplama modülü bulunmaktadır.

Yönetim Paneli

Yönetim paneli, sistem içerisindeki operasyonların merkezi olarak yönetilmesini sağlamaktadır.

Panel üzerinden;

Kullanıcı yönetimi
Kargo yönetimi
Şube yönetimi
Kurye yönetimi
Kargo arama ve filtreleme
Kargo durum takibi
İstatistiklerin görüntülenmesi
Kurye performans bilgilerinin takibi gerçekleştirilebilmektedir.
Kargo durumları, aylık kargo dağılımları, şube bazlı veriler ve kurye performansları Chart.js kullanılarak grafikler üzerinden görselleştirilmektedir.

Teknoloji Yığını
Backend
Python
Flask
Flask-SQLAlchemy
Jinja2
Frontend
HTML5
CSS3
JavaScript
Bootstrap
Chart.js
Iconify
Veritabanı
PostgreSQL
Sistem Mimarisi

Uygulama Flask tabanlı backend, Jinja2 tabanlı frontend ve PostgreSQL ilişkisel veritabanı üzerine kurulmuştur.
Veritabanı işlemleri SQLAlchemy aracılığıyla gerçekleştirilmekte ve kullanıcıların sistem içerisindeki erişimleri rol bazlı yetkilendirme mekanizması ile kontrol edilmektedir.

Veritabanı Yapısı
Sistemin temel tabloları aşağıdaki gibidir:

roller
kullanicilar
subeler
kuryeler
sube_personelleri
kargolar
kargo_hareketleri

Bu tablolar arasındaki ilişkiler sayesinde kullanıcı, rol, şube, kurye, kargo ve kargo hareketleri arasındaki veri bütünlüğü sağlanmaktadır.
