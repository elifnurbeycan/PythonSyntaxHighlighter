# Gerçek Zamanlı Sözdizimi Vurgulayıcı (Syntax Highlighter) – GUI Uygulaması

## 📌 Genel Bakış

Bu proje, bir **programlama dili** için gerçek zamanlı çalışan, **grafiksel kullanıcı arayüzü (GUI)** içeren bir **sözdizimi vurgulayıcı** uygulamasıdır. Geliştirilen sistem, **biçimsel dil kurallarına (gramer)** dayalı olarak **leksik (lexical) ve sözdizimsel (syntax) analiz** gerçekleştirir.

Proje kapsamında hiçbir hazır vurgulama (highlighting) kütüphanesi kullanılmamış, tüm analiz araçları sıfırdan geliştirilmiştir.

## 🚀 Özellikler

- Tkinter tabanlı kullanıcı dostu grafik arayüzü
- Kod yazılırken gerçek zamanlı sözdizimi vurgulaması
- En az 5 farklı token türünü anlık olarak ayırt edip renklendirme
- Regex tabanlı programatik leksik analiz
- Recursive Descent (Top-Down) parser ile sözdizimsel analiz
- Hatalı sözdizimi kullanıcıya anlık olarak gösterme
- Kod bloklarını girintiye göre algılama ve ayrıştırma
- Harici herhangi bir sözdizimi vurgulama kütüphanesi kullanılmaz

## 🧩 Desteklenen Token Türleri ve Yapılar

Bu uygulama, aşağıdaki Python sözdizimi öğelerini tanır ve vurgular:

- **Anahtar Kelimeler:** `if`, `else`, `while`, `def`, `return`, `and`, `or`, `not` vb.
- **Operatörler:** `=`, `==`, `+`, `-`, `*`, `/`, `%`, `!=`, `<`, `>`, `<=`, `>=` vb.
- **Sayılar:** Tam sayılar, ondalıklı sayılar
- **Dizeler:** Tek tırnak veya çift tırnak içinde metinler
- **Yorumlar:** Satır içi `#` ile başlayan açıklamalar
- **Tanımlayıcılar:** Değişken ve fonksiyon isimleri
- **Boolean Değerleri:** `True`, `False`, `None`
- **Fonksiyon Çağrıları:** Örnek: `print(x)`
- **Kod Blokları:** Girinti ile belirlenen bloklar (if, while, fonksiyon vb.)
- **Parantezler, Virgüller, İki Nokta (:)** gibi yapısal semboller
- **Hatalı Karakterler:** Tanınmayan veya yanlış yazılmış semboller

## 🎨 Vurgulama Renkleri

| Token Türü       | Renk          |
|------------------|---------------|
| Anahtar Kelime   | Mavi          |
| Tanımlayıcı      | Siyah         |
| Sayı             | Turuncu       |
| Operatör         | Kırmızı       |
| Sembol           | Gri           |
| Yorum            | Yeşil         |
| Dize             | Mor           |
| Boolean Değerleri| Koyu Mavi     |
| Hatalı Karakter  | Kırmızı (Altı Çizili) |

## 🖼 Arayüz (GUI)

- Python Tkinter kullanılarak oluşturuldu
- Kullanıcı yazdıkça sözdizimi anında güncellenir ve renklendirilir
- Hatalı sözdiziminde görsel uyarı
- (Opsiyonel) AST yapısını görselleştirme desteği

## 📄 Dokümantasyon

Projeyle ilgili tüm teknik bilgiler ve kararlar aşağıdaki makalede açıklanmıştır:

📝 [Projeye ait teknik makale - Bağlantı eklenecek](#)

### İçerik

- Dil ve gramer seçimi
- Leksik analiz süreci ve yöntemleri
- Parser yapısı ve kuralları
- Sözdizimi vurgulama mantığı
- GUI tasarımı ve işleyişi

## 📹 Tanıtım Videosu

Uygulamanın çalışma prensibini ve özelliklerini anlatan video:

▶️ [Tanıtım Videosu - Bağlantı eklenecek](#)

## 📦 Kurulum ve Kullanım

```bash
# Projeyi klonlayın
git clone https://github.com/elifnurbeycanz/PythonSyntaxHighlighter.git
cd PythonSyntaxHighlighter

# Uygulamayı başlatın
python main.py
