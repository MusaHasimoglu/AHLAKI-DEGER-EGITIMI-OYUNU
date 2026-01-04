# 🎓 Ahlaki Değer Eğitimi Oyunu

## 👋 Giriş ve Hakkımda
Merhaba! Ben **Musa Haşimoğlu**. Ankara Üniversitesi, Bilgisayar ve Öğretim Teknolojileri Öğretmenliği (BÖTE) bölümü 2. sınıf öğrencisiyim. Bu proje, teknolojiyi eğitimle harmanlayarak toplumsal değerlerin dijital bir ortamda nasıl kazandırılabileceğini göstermek amacıyla hazırladığım bir "Eğitsel Oyun" çalışmasıdır.

Günümüzde değerler eğitiminin önemi artarken, bu süreci oyunlaştırma (gamification) ile destekleyerek öğrencilerin etik ikilemler karşısında kendi kararlarını vermelerini ve bu kararların sonuçlarını güvenli bir simülasyonda tecrübe etmelerini hedefledim.

## 📝 Proje Özeti
"Ahlaki Değer Eğitimi Oyunu", Python ve Pygame kütüphanesi kullanılarak geliştirilmiş, 10 farklı seviyeden oluşan bir rol yapma oyunudur. Oyunda dürüstlük, yardımseverlik, empati ve sorumluluk gibi temel değerler; dallanan diyaloglar ve senaryolar üzerinden işlenmektedir.

## 🎮 Bölümler ve Ahlaki Kazanımlar
Oyunun her bir seviyesi belirli bir temel değer üzerine kurgulanmıştır:

| Bölüm | Mekan | Ahlaki Tema / Kazanım |
| :--- | :--- | :--- |
| **Bölüm 1** | Otobüs Durağı | Sıra Kültürü ve Başkalarının Haklarına Saygı |
| **Bölüm 2** | Sınav Salonu | Akademik Dürüstlük ve Sınav Etiği |
| **Bölüm 3** | Okul Çıkışı | Finansal Sorumluluk ve Borç Sadakati |
| **Bölüm 4** | Kütüphane | Ortak Alan Kullanımı ve Başkalarını Rahatsız Etmeme |
| **Bölüm 5** | Market | Ticari Dürüstlük (Fazla Para Üstü İkilemi) |
| **Bölüm 6** | Trafik | Yaya Hakları ve Trafikte Nezaket |
| **Bölüm 7** | Genç Odası | Kişisel Verilerin Gizliliği (Bilgi Paylaşımı) |
| **Bölüm 8** | Sokak | Sahipsiz Eşya Karşısında Dürüstlük ve Empati |
| **Bölüm 9** | Park | Çevre Bilinci ve Doğal Kaynakların Korunması |
| **Bölüm 10** | Okul Bahçesi | Akran Zorbalığıyla Mücadele ve Dayanışma (Final) |

## 🛠️ Teknik Mimari ve Özellikler
* **Programlama Dili:** Python 3.x
* **Kütüphane:** Pygame
* **OOP Mimari:** `BaseLevel` ata sınıfı üzerinden kalıtım (inheritance) ve metod ezme (overriding) kullanılmıştır.
* **Veri Yönetimi:** Diyalog ağaçları **JSON** formatında dinamik olarak yönetilmektedir.
* **Algoritma:** Özel **Metin Sarma (Text-Wrapping)** algoritması uygulanmıştır.

## 🚀 Kurulum ve Başlatma

### 1. Projeyi Yerel Bilgisayara Yükleme
Projeyi kendi bilgisayarınıza indirmek için terminale şu komutu yazın:
```bash
git clone https://github.com/MusaHasimoglu/AHLAKI-DEGER-EGITIMI-OYUNU.git
```

### 2. Gerekli Kütüphanelerin Yüklenmesi
Sisteminizde Python yüklü olduğundan emin olduktan sonra Pygame kütüphanesini kurun
```bash 
pip install pygame
```

### 3. Oyunu Çalıştırma
Proje klasörüne girin ve ana dosyayı şu komutla başlatın
```bash 
python main.py
```