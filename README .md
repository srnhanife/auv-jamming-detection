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
- M. Stojanovic, J. Preisig, "Underwater acoustic communication channels: Propagation models and statistical characterization," *IEEE Communications Magazine*, 47(1), 2009.

## Yapay Zekâ Kullanım Beyanı
`src/kanal_modeli.py` ve `src/senaryolar.py` dosyalarının ilk sürümü YZ aracı (Claude, Anthropic) desteğiyle
yazılmıştır. Kodun tamamı tarafımca okunmuş, çalıştırılmış ve sonuçları teorik değerlerle karşılaştırılarak
kontrol edilmiştir. Parametre seçimleri ve yorumlar tarafıma aittir.
