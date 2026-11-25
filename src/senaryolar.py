"""
senaryolar.py
Normal haberleşme (S0) ve üç karıştırma senaryosunun (S1-S3) paket düzeyinde simülasyonu.

  S0: Normal haberleşme (karıştırma yok)
  S1: Sabit karıştırma       - karıştırıcı her pakette açık
  S2: Rastgele aralıklı      - karıştırıcı her pakette belirli olasılıkla açık
  S3: Frekans taramalı       - dar bantlı karıştırıcı frekansını zamanla tarar,
                               sinyal bandıyla örtüştüğü ölçüde etkili olur

Modülasyon: BPSK. Bit hızı = bant genişliği kabul edildi, böylece Eb/N0 = SINR.
Basitleştirme: Karıştırma sinyali alıcıda Gauss gürültüsü gibi davranıyor kabul edildi.
Not: Bu dosya YZ (Claude) desteğiyle yazılmış, tarafımca okunup test edilmiştir.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import erfc

from kanal_modeli import iletim_kaybi, ortam_gurultusu

# ------------------------- PARAMETRELER -------------------------
RNG = np.random.default_rng(42)   # sabit tohum: sonuçlar her çalıştırmada aynı çıkar
FC_KHZ = 12.0        # merkez frekans (kHz)
B_HZ = 4000          # sinyal bant genişliği (Hz) -> sinyal bandı 10-14 kHz
SL_VERICI = 150      # verici AUV kaynak seviyesi (dB re 1 µPa @ 1 m)
D_VERICI = 2000      # verici - alıcı mesafesi (m)
SL_KARISTIRICI = 150 # saldırgan AUV kaynak seviyesi (dB)
D_KARISTIRICI = 3000 # saldırgan - alıcı mesafesi (m)
GOLGELEME_DB = 2.0   # paketten pakete kanal dalgalanması (std, dB)
PAKET_BIT = 256      # paket uzunluğu (bit)
PAKET_SAYISI = 500   # her senaryo için paket sayısı
S2_ACIK_OLASILIK = 0.4   # S2: karıştırıcının açık olma olasılığı
S3_BANT_HZ = 2000        # S3: karıştırıcının dar bant genişliği
S3_TARAMA = (6000, 18000)  # S3: taranan frekans aralığı (Hz)
S3_PERIYOT = 25            # S3: bir tam tarama kaç pakette tamamlanır


def db2lin(x): return 10 ** (np.asarray(x) / 10)
def lin2db(x): return 10 * np.log10(x)


def teorik_ber_bpsk(ebn0_db):
    """BPSK için teorik bit hata oranı: 0.5 * erfc(sqrt(Eb/N0))."""
    return 0.5 * erfc(np.sqrt(db2lin(ebn0_db)))


def bpsk_gonder(sinr_db, n_bit):
    """n_bit uzunluğunda BPSK paketi gönderir, hatalı bit sayısını döndürür."""
    bitler = RNG.integers(0, 2, n_bit)
    sembol = 2 * bitler - 1                         # 0 -> -1, 1 -> +1
    sigma = np.sqrt(1 / (2 * db2lin(sinr_db)))      # Eb = 1 için gürültü std
    alinan = sembol + sigma * RNG.standard_normal(n_bit)
    karar = (alinan > 0).astype(int)
    return int(np.sum(karar != bitler))


def s3_ortusme_orani(paket_no):
    """S3: karıştırıcı bandının sinyal bandıyla örtüşen kısmının oranı (0-1)."""
    alt, ust = S3_TARAMA
    faz = (paket_no % S3_PERIYOT) / S3_PERIYOT
    j_merkez = alt + faz * (ust - alt)
    j_alt, j_ust = j_merkez - S3_BANT_HZ / 2, j_merkez + S3_BANT_HZ / 2
    s_alt, s_ust = FC_KHZ * 1000 - B_HZ / 2, FC_KHZ * 1000 + B_HZ / 2
    ortusme = max(0.0, min(j_ust, s_ust) - max(j_alt, s_alt))
    return ortusme / S3_BANT_HZ


def senaryo_calistir(kod):
    """Bir senaryoyu çalıştırır, paket bazında kayıt listesini döndürür."""
    S = SL_VERICI - iletim_kaybi(D_VERICI, FC_KHZ)                          # alınan sinyal (dB)
    N = ortam_gurultusu(FC_KHZ) + 10 * np.log10(B_HZ)                        # bant içi gürültü (dB)
    J = SL_KARISTIRICI - iletim_kaybi(D_KARISTIRICI, FC_KHZ)                 # alınan karıştırma (dB)

    kayitlar = []
    for p in range(PAKET_SAYISI):
        S_p = S + RNG.normal(0, GOLGELEME_DB)        # kanal dalgalanması
        if kod == "S0":
            I_lin = 0.0
        elif kod == "S1":
            I_lin = db2lin(J)
        elif kod == "S2":
            I_lin = db2lin(J) if RNG.random() < S2_ACIK_OLASILIK else 0.0
        elif kod == "S3":
            I_lin = db2lin(J) * s3_ortusme_orani(p)
        snr = S_p - N
        sinr = lin2db(db2lin(S_p) / (db2lin(N) + I_lin))
        hata = bpsk_gonder(sinr, PAKET_BIT)
        kayitlar.append({
            "senaryo": kod, "paket": p,
            "snr_db": round(snr, 3), "sinr_db": round(sinr, 3),
            "hatali_bit": hata, "ber": hata / PAKET_BIT,
            "teslim": int(hata == 0),             # hatasız paket teslim edildi sayılır
            "etiket": 0 if kod == "S0" else 1,    # 0 = normal, 1 = saldırı
        })
    return kayitlar


def dogrulama_grafigi():
    """S0 doğrulaması: simülasyon BER'i ile teorik BPSK BER'inin karşılaştırılması."""
    ebn0 = np.arange(0, 11, 1)
    n = 2_000_000   # yüksek Eb/N0 de yeterli hata sayısı için çok bit gerekir
    sim = [bpsk_gonder(e, n) / n for e in ebn0]
    plt.figure(figsize=(7, 4.5))
    e_ince = np.linspace(0, 10, 200)
    plt.semilogy(e_ince, teorik_ber_bpsk(e_ince), label="Teorik BPSK")
    plt.semilogy(ebn0, np.maximum(sim, 1e-7), "o", label="Simülasyon")
    plt.xlabel("Eb/N0 (dB)"); plt.ylabel("BER")
    plt.title("Doğrulama: simülasyon ve teorik BPSK BER")
    plt.grid(alpha=0.3, which="both"); plt.legend()
    plt.tight_layout(); plt.savefig("sonuclar/3_ber_dogrulama.png", dpi=150)
    for e, s in zip(ebn0, sim):
        print(f"  Eb/N0={e:2d} dB  simülasyon={s:.2e}  teorik={teorik_ber_bpsk(e):.2e}")


if __name__ == "__main__":
    os.makedirs("sonuclar", exist_ok=True)

    print("1) Doğrulama (S0, BPSK):")
    dogrulama_grafigi()

    print("\n2) Senaryolar çalıştırılıyor...")
    tum = []
    for kod in ("S0", "S1", "S2", "S3"):
        tum += senaryo_calistir(kod)
    df = pd.DataFrame(tum)
    df.to_csv("sonuclar/on_veri.csv", index=False)

    ozet = df.groupby("senaryo").agg(
        ort_snr_db=("snr_db", "mean"), ort_sinr_db=("sinr_db", "mean"),
        ort_ber=("ber", "mean"), pdr=("teslim", "mean"))
    ozet["paket_kaybi"] = 1 - ozet["pdr"]
    print(ozet.round(4).to_string())
    ozet.round(4).to_csv("sonuclar/senaryo_ozeti.csv")

    # Grafik: paket bazında SINR'nin zamanla değişimi
    fig, eksen = plt.subplots(4, 1, figsize=(8, 7), sharex=True, sharey=True)
    adlar = {"S0": "S0 Normal", "S1": "S1 Sabit", "S2": "S2 Rastgele aralıklı", "S3": "S3 Frekans taramalı"}
    for ax, kod in zip(eksen, adlar):
        alt = df[df.senaryo == kod].head(100)
        ax.plot(alt.paket, alt.sinr_db, lw=1)
        ax.set_title(adlar[kod], fontsize=9, loc="left"); ax.grid(alpha=0.3)
        ax.set_ylabel("SINR (dB)")
    eksen[-1].set_xlabel("Paket no")
    plt.tight_layout(); plt.savefig("sonuclar/4_sinr_zaman.png", dpi=150)

    # Grafik: senaryolara göre PDR ve ortalama BER
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
    a1.bar(ozet.index, ozet.pdr); a1.set_title("Paket teslim oranı (PDR)"); a1.set_ylim(0, 1.05)
    a2.bar(ozet.index, ozet.ort_ber); a2.set_title("Ortalama BER")
    for a in (a1, a2): a.grid(alpha=0.3, axis="y")
    plt.tight_layout(); plt.savefig("sonuclar/5_senaryo_karsilastirma.png", dpi=150)

    print("\nGrafikler ve on_veri.csv 'sonuclar' klasörüne kaydedildi.")
