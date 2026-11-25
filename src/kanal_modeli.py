"""
kanal_modeli.py
Sualtı akustik kanal modeli: Thorp soğurması, iletim kaybı, ortam gürültüsü ve SNR.

Kaynak formüller:
  - Thorp soğurma katsayısı ve ortam gürültüsü (türbülans, gemi, rüzgâr, termal):
    M. Stojanovic & J. Preisig, IEEE Communications Magazine, 2009 (ara rapor [2]).
Not: Bu dosya YZ (Claude) desteğiyle yazılmış, tarafımca okunup test edilmiştir.
"""
import numpy as np


def thorp_sogurma(f_khz):
    """Thorp soğurma katsayısı [dB/km]. f_khz: frekans (kHz)."""
    f2 = f_khz ** 2
    return 0.11 * f2 / (1 + f2) + 44 * f2 / (4100 + f2) + 2.75e-4 * f2 + 0.003


def iletim_kaybi(d_m, f_khz, k=1.5):
    """
    İletim kaybı TL [dB] = yayılma kaybı + soğurma kaybı.
    d_m : mesafe (metre), f_khz : frekans (kHz)
    k   : yayılma katsayısı (1 = silindirik, 2 = küresel, 1.5 = pratik değer)
    """
    yayilma = k * 10 * np.log10(d_m)              # 1 m referansına göre
    sogurma = (d_m / 1000) * thorp_sogurma(f_khz)  # dB/km * km
    return yayilma + sogurma


def ortam_gurultusu(f_khz, gemi=0.5, ruzgar_ms=5.0):
    """
    Ortam gürültüsü güç spektral yoğunluğu [dB re 1 µPa^2/Hz].
    gemi: gemi trafiği yoğunluğu (0-1), ruzgar_ms: rüzgâr hızı (m/s)
    Dört bileşen güç olarak (dB değil!) toplanır.
    """
    f = f_khz
    Nt = 17 - 30 * np.log10(f)                                                   # türbülans
    Ns = 40 + 20 * (gemi - 0.5) + 26 * np.log10(f) - 60 * np.log10(f + 0.03)     # gemi
    Nw = 50 + 7.5 * np.sqrt(ruzgar_ms) + 20 * np.log10(f) - 40 * np.log10(f + 0.4)  # rüzgâr
    Nth = -15 + 20 * np.log10(f)                                                 # termal
    toplam = 10 ** (Nt / 10) + 10 ** (Ns / 10) + 10 ** (Nw / 10) + 10 ** (Nth / 10)
    return 10 * np.log10(toplam)


def snr_db(d_m, f_khz, kaynak_seviyesi_db, bant_genisligi_hz, gemi=0.5, ruzgar_ms=5.0):
    """
    Pasif sonar denklemi: SNR = SL - TL - (NL + 10log10(B))
    kaynak_seviyesi_db: verici kaynak seviyesi SL [dB re 1 µPa @ 1 m]
    """
    TL = iletim_kaybi(d_m, f_khz)
    NL = ortam_gurultusu(f_khz, gemi, ruzgar_ms) + 10 * np.log10(bant_genisligi_hz)
    return kaynak_seviyesi_db - TL - NL


if __name__ == "__main__":
    # Bu dosya doğrudan çalıştırılırsa kanal modelinin grafiklerini çizer.
    import os
    import matplotlib.pyplot as plt

    os.makedirs("sonuclar", exist_ok=True)
    d = np.linspace(100, 10000, 300)   # 100 m - 10 km

    # Grafik 1: farklı frekanslarda iletim kaybı
    plt.figure(figsize=(7, 4.5))
    for f in (5, 12, 25, 50):
        plt.plot(d / 1000, iletim_kaybi(d, f), label=f"{f} kHz")
    plt.xlabel("Mesafe (km)"); plt.ylabel("İletim kaybı TL (dB)")
    plt.title("Thorp modeline göre iletim kaybı (k = 1.5)")
    plt.grid(alpha=0.3); plt.legend()
    plt.tight_layout(); plt.savefig("sonuclar/1_iletim_kaybi.png", dpi=150)

    # Grafik 2: mesafeye göre SNR (fc = 12 kHz, B = 4 kHz, SL = 150 dB)
    plt.figure(figsize=(7, 4.5))
    plt.plot(d / 1000, snr_db(d, 12, 150, 4000))
    plt.axhline(0, color="gray", ls="--", lw=1)
    plt.xlabel("Mesafe (km)"); plt.ylabel("SNR (dB)")
    plt.title("Normal haberleşmede mesafeye göre SNR (fc=12 kHz, B=4 kHz)")
    plt.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("sonuclar/2_snr_mesafe.png", dpi=150)

    # Kontrol için birkaç sayısal değer
    print("Thorp soğurma @12 kHz :", round(thorp_sogurma(12), 3), "dB/km")
    for km in (1, 2, 3, 5):
        print(f"d = {km} km -> TL = {iletim_kaybi(km*1000, 12):.1f} dB, SNR = {snr_db(km*1000, 12, 150, 4000):.1f} dB")
    print("Grafikler 'sonuclar' klasörüne kaydedildi.")
