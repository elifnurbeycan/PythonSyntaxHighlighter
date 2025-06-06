# Gerçek Zamanlı Sözdizimi Vurgulayıcı (Syntax Highlighter) – GUI Uygulaması

## 📌 Genel Bakış

Bu proje, bir **programlama dili** için gerçek zamanlı çalışan, **grafiksel kullanıcı arayüzü (GUI)** içeren bir **sözdizimi vurgulayıcı** uygulamasıdır. Geliştirilen sistem, **biçimsel dil kurallarına (gramer)** dayalı olarak **leksik (lexical) ve sözdizimsel (syntax) analiz** gerçekleştirir.

Proje kapsamında hiçbir hazır vurgulama (highlighting) kütüphanesi kullanılmamış, tüm analiz araçları sıfırdan geliştirilmiştir.

## 🚀 Özellikler

- ✅ Gerçek zamanlı sözdizimi vurgulama
- ✅ En az 5 farklı türde token (birim) vurgulaması
- ✅ Durum diyagramına dayalı leksik analiz
- ✅ Top-down (yukarıdan aşağı) sözdizim analiz yöntemi
- ✅ Kullanıcı dostu grafik arayüz (Tkinter)
- ✅ Kamuya açık tanıtım videosu ve teknik makale

## 🔧 Kullanılan Teknolojiler

- **Programlama Dili:** Python
- **Arayüz Kütüphanesi:** Tkinter
- **Lexical Analyzer:** Durum diyagramına dayalı programatik yaklaşım
- **Parser Türü:** Top-Down (Recursive Descent)
- **Token Türleri:** Anahtar kelime, tanımlayıcı, işlemci, sayı, sembol

## 🧠 Sözdizimi Analizi

### Leksik Analiz (Lexical Analysis)

- Giriş metni, belirlenen kurallara göre parçalara (token) ayrılır.
- Kullanılan token türleri:
  - **Anahtar kelimeler:** `if`, `while`, `return` gibi
  - **Tanımlayıcılar:** değişken ve fonksiyon adları
  - **İşlemciler:** `+`, `-`, `=`, vb.
  - **Sayılar:** sayısal değerler
  - **Semboller:** `{`, `}`, `(`, `)`, vb.

### Sözdizimsel Analiz (Syntax Analysis)

- **Top-Down (yukarıdan aşağı)** yaklaşımıyla, bir **Recursive Descent Parser** kullanılır.
- Tanımlı bağlamdan bağımsız gramer kurallarına göre analiz yapılır.
- Hatalı sözdizimi, gerçek zamanlı olarak kullanıcıya bildirilir.

## 🎨 Vurgulama Sistemi

| Token Türü   | Renk          |
|--------------|---------------|
| Anahtar Kelime | Mavi         |
| Tanımlayıcı    | Siyah        |
| Sayı           | Turuncu      |
| İşlemci        | Kırmızı      |
| Sembol         | Gri          |

## 🖼 Arayüz (GUI)

Uygulama, Python’un Tkinter kütüphanesi ile geliştirilmiştir. Özellikleri:

- Kullanıcı yazdıkça gerçek zamanlı vurgulama
- Her token türü için farklı renk
- Hatalı sözdiziminde uyarı
- (Opsiyonel) Sözdizimi ağacı (AST) gösterimi

## 📄 Dokümantasyon

Projeyle ilgili tüm teknik bilgiler ve kararlar aşağıdaki makalede açıklanmıştır:

📝 [Projeye ait yazı - Bağlantı eklenecek](#)

### İçerik:

- Gramer tanımı ve tercih nedenleri
- Leksik analiz süreci
- Parser yapısı ve kurallar
- Vurgulama sistemi mantığı
- Arayüz tasarımı ve işlevselliği

## 📹 Tanıtım Videosu

Uygulamanın nasıl çalıştığını gösteren tanıtım videosuna aşağıdan ulaşabilirsiniz:

▶️ [Tanıtım Videosu - Bağlantı eklenecek](#)

## 📦 Kurulum ve Kullanım

```bash
# Projeyi klonla
git clone https://github.com/elifnurbeycanz/PythonSyntaxHighlighter.git
cd PythonSyntaxHighlighter

# Uygulamayı çalıştır
python main.py
