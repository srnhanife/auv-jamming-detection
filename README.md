# Otonom Sualtı Araçlarında Akustik Karıştırma Saldırılarının Analizi ve ML Tabanlı Tespiti

**Bitirme Tezi (CEN 401 / CEN 402) – Recep Tayyip Erdoğan Üniversitesi, Bilgisayar Mühendisliği**
**Takım Kodu:** YYI-1063 · **Öğrenci:** Hanife ŞİRİN (231401063) · **Danışman:** Dr. Öğr. Üyesi Yıldıran Yılmaz

Bu depo, sualtı akustik haberleşmesinde karıştırma (jamming) saldırılarının etkisini simüle eden
ve ileride makine öğrenmesiyle tespit için veri üreten Python kodlarını içerir.

## Mevcut durum (Ön Çalışma – Güz H8–H10)
- [x] Akustik kanal modeli: Thorp soğurması, iletim kaybı, ortam gürültüsü, SNR
- [x] Normal haberleşme (S0) için BPSK simülasyonu ve teorik BER ile **doğrulama**
- [x] Karıştırma senaryoları: S1 sabit, S2 rastgele aralıklı, S3 frekans taramalı
- [x] Paket bazında ön veri kümesi (`sonuclar/on_veri.csv`)
- [ ] Gecikme ölçütü, çok yollu yayılım (Bahar B2–B4)
- [ ] Eşik tabanlı model, SVM ve Random Forest ile tespit (Bahar B5–B6)

## Klasör yapısı
```
src/kanal_modeli.py   Kanal modeli (iletim kaybı, gürültü, SNR) + grafikler
src/senaryolar.py     S0–S3 senaryoları, doğrulama, ön veri kümesi + grafikler
sonuclar/             Üretilen grafikler (.png) ve veri (.csv)
requirements.txt      Gerekli kütüphaneler
```

## Kurulum ve çalıştırma
Python 3.10 veya üstü gerekir (geliştirmede 3.14.3 kullanıldı).
```bash
py -m pip install -r requirements.txt
py src/kanal_modeli.py
py src/senaryolar.py
```
Komutlar depo ana klasöründen çalıştırılmalıdır; çıktılar `sonuclar/` klasörüne yazılır.

## Ön Bulgular
Aşağıdaki değerler `py src/kanal_modeli.py` ve `py src/senaryolar.py` komutlarının çıktısıdır
(rastgelelik tohumu sabit: `seed = 42`, sonuçlar her çalıştırmada aynı çıkar).

**1. Kanal modeli (fc = 12 kHz, B = 4 kHz, SL = 150 dB)**
- Thorp soğurma katsayısı (12 kHz): **1.645 dB/km**
- Mesafeye göre SNR: 1 km → **22.7 dB**, 2 km → **16.6 dB**, 3 km → **12.3 dB**, 5 km → **5.7 dB**

**2. Doğrulama: simülasyon ve teorik BPSK BER karşılaştırması** (`sonuclar/3_ber_dogrulama.png`)
- Eb/N0 = 0–8 dB aralığında simülasyon ile teorik BER arasındaki en büyük bağıl fark **%3.1**
  (örnek: 4 dB'de simülasyon 1.25×10⁻², teorik 1.25×10⁻²).
- 9–10 dB'de fark %14–16'ya çıkıyor. Bu, BER'in 10⁻⁵ düzeyine inmesiyle 2×10⁶ bitte
  yalnızca 9–58 hata gözlenmesinden kaynaklanan istatistiksel bir sapmadır.

**3. Karıştırma senaryolarında haberleşme başarımı** (senaryo başına 500 paket, `sonuclar/senaryo_ozeti.csv`)

| Senaryo | Ort. SNR (dB) | Ort. SINR (dB) | Ort. BER | PDR | Paket kaybı |
|---|---|---|---|---|---|
| S0 Normal | 16.50 | 16.50 | 0.0000 | **1.000** | 0.000 |
| S1 Sabit | 16.47 | 3.95 | 0.0210 | **0.186** | 0.814 |
| S2 Rastgele aralıklı | 16.59 | 11.38 | 0.0071 | **0.684** | 0.316 |
| S3 Frekans taramalı | 16.42 | 11.37 | 0.0064 | **0.734** | 0.266 |

- SNR tüm senaryolarda aynı kalırken SINR düşüyor. Ortam gürültüsü değişmiyor; düşüş karıştırmadan kaynaklanıyor.
- En yıkıcı senaryo sabit karıştırma (S1). S2 ve S3'te karıştırma yalnızca belirli paketleri etkiliyor
  (`sonuclar/4_sinr_zaman.png`).

**4. Ön veri kümesi** (`sonuclar/on_veri.csv`)
- Toplam **2000 örnek** (paket): 500 normal (etiket 0), 1500 saldırı (etiket 1)
- Sütunlar: `senaryo, paket, snr_db, sinr_db, hatali_bit, ber, teslim, etiket`
- Not: Sınıflar dengesiz (1:3). Bahar döneminde model eğitiminde dikkate alınacak.

## Temel parametreler
| Parametre | Değer |
|---|---|
| Merkez frekans / bant genişliği | 12 kHz / 4 kHz |
| Verici kaynak seviyesi, mesafe | 150 dB re 1 µPa, 2 km |
| Karıştırıcı kaynak seviyesi, mesafe | 150 dB re 1 µPa, 3 km |
| Modülasyon, paket uzunluğu | BPSK, 256 bit |
| Paket sayısı (senaryo başına) | 500 |

## Varsayımlar ve sınırlılıklar
- Bit hızı bant genişliğine eşit kabul edildi (Eb/N0 = SINR).
- Karıştırma sinyali alıcıda Gauss gürültüsü gibi modellendi.
- Çok yollu yayılım henüz modellenmedi; paketler arası kanal değişimi 2 dB log-normal gölgeleme ile temsil edildi.
- Bir paket, hiç bit hatası yoksa teslim edilmiş sayıldı.

## Kaynaklar
Köşeli parantez içindeki numaralar, ara rapordaki (YYI-1063 Ara Rapor) kaynakça numaralarıdır.

**Akustik kanal modeli (`kanal_modeli.py`)**
- [1] I. F. Akyildiz, D. Pompili, T. Melodia, "Underwater acoustic sensor networks: research challenges," *Ad Hoc Networks*, vol. 3, no. 3, pp. 257–279, 2005. DOI: [10.1016/j.adhoc.2005.01.004](https://doi.org/10.1016/j.adhoc.2005.01.004)
  → Sualtı akustik kanalının temel kısıtları: düşük ses hızı (≈1500 m/s), dar bant genişliği, yüksek gecikme.
- [2] M. Stojanovic, J. Preisig, "Underwater acoustic communication channels: Propagation models and statistical characterization," *IEEE Communications Magazine*, vol. 47, no. 1, pp. 84–89, 2009. DOI: [10.1109/MCOM.2009.4752682](https://doi.org/10.1109/MCOM.2009.4752682)
  → Thorp soğurma katsayısı, iletim kaybı (yayılma katsayısı k = 1.5) ve ortam gürültüsü (türbülans, gemi, rüzgâr, termal) formülleri.
- [3] M. A. Çavuşlu, M. Altuncu, H. Özcan, F. Kaya Gülağiz, S. Şahin, "Sualtı Haberleşmede Çok Yolluluğun Bant Genişliği, Kapasite ve İletim Gücü Üzerindeki Etkisi," *Bilecik Şeyh Edebali Üniversitesi Fen Bilimleri Dergisi*, vol. 7, no. 1, pp. 404–420, 2020. DOI: [10.35193/bseufbd.706560](https://doi.org/10.35193/bseufbd.706560)
  → Çok yollu yayılımın etkisi; Bahar döneminde modele eklenecek bileşen (README "Varsayımlar" bölümü).

**Karıştırma senaryoları (`senaryolar.py`)**
- [7] S. Jiang, "On Securing Underwater Acoustic Networks: A Survey," *IEEE Communications Surveys & Tutorials*, vol. 21, no. 1, pp. 729–752, 2019. DOI: [10.1109/COMST.2018.2864127](https://doi.org/10.1109/COMST.2018.2864127)
  → Sualtı ağlarında karıştırma saldırılarının sınıflandırılması.
- [8] M. Zuba, Z. Shi, Z. Peng, J. Cui, S. Zhou, "Vulnerabilities of underwater acoustic networks to denial-of-service jamming attacks," *Security and Communication Networks*, vol. 8, no. 16, pp. 2635–2645, 2015. DOI: [10.1002/sec.507](https://doi.org/10.1002/sec.507)
  → Sabit (S1) ve rastgele aralıklı (S2) karıştırma türleri ve paket teslim oranına etkisi.
- [9] A. Signori, F. Chiariotti, F. Campagnaro, M. Zorzi, "A Game-Theoretic and Experimental Analysis of Energy-Depleting Underwater Jamming Attacks," *IEEE Internet of Things Journal*, vol. 7, no. 10, pp. 9793–9804, 2020. DOI: [10.1109/JIOT.2020.2982613](https://doi.org/10.1109/JIOT.2020.2982613)
  → Karıştırıcının enerji kısıtı nedeniyle aralıklı çalışması (S2 için gerekçe).
- [10] W. Aman, S. Al-Kuwari, M. Qaraqe, "Performance Analysis of Underwater Acoustic Channel Amid Jamming by Random Jammers," *Internet Technology Letters*, vol. 8, no. 4, p. e595, 2025. Ön baskı: [arXiv:2405.02885](https://arxiv.org/abs/2405.02885)
  → Rastgele karıştırıcılar altında kanal başarımının analizi; SINR tabanlı değerlendirme.

**Saldırı tespiti (Bahar dönemi)**
- [11] S. Rajasoundaran vd., "Secure and optimized intrusion detection scheme using LSTM-MAC principles for underwater wireless sensor networks," *Wireless Networks*, vol. 30, no. 1, pp. 209–231, 2024. DOI: [10.1007/s11276-023-03470-x](https://doi.org/10.1007/s11276-023-03470-x)
  → LSTM tabanlı tespit (isteğe bağlı olarak değerlendirilecek).
- [12] J. S. Mertens, A. Panebianco, A. Surudhi, N. Prabagarane, L. Galluccio, "Network intelligence vs. jamming in underwater networks: how learning can cope with misbehavior," *Frontiers in Communications and Networks*, vol. 4, p. 1179626, 2023. DOI: [10.3389/frcmn.2023.1179626](https://doi.org/10.3389/frcmn.2023.1179626)
  → Öğrenme tabanlı yöntemlerle karıştırmaya karşı tespit ve tepki.

## Yapay Zekâ Kullanım Beyanı
`src/kanal_modeli.py` ve `src/senaryolar.py` dosyalarının ilk sürümü YZ aracı (Claude, Anthropic) desteğiyle
yazılmıştır. Kodun tamamı tarafımca okunmuş, çalıştırılmış ve sonuçları teorik değerlerle karşılaştırılarak
kontrol edilmiştir. Parametre seçimleri ve yorumlar tarafıma aittir.
