import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

# Set konfigurasi halaman agar terlihat lebih lebar (opsional)
st.set_page_config(layout="centered")

# --- Bagian Styling CSS untuk Meniru Tampilan Gambar ---
# CSS untuk container utama (background dan padding)
# Anda bisa menyesuaikan warna gradient sesuai kebutuhan
custom_css = """
<style>
.ferizy-container {
    background: linear-gradient(180deg, #1A73E8 0%, #1A73E8 30%, #4285F4 60%, #FFFFFF 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    margin-bottom: 20px;
}

.ferizy-header {
    font-size: 2.5em;
    font-weight: 700;
    margin-bottom: 5px;
    line-height: 1.0;
}

.ferizy-subheader {
    font-size: 1.5em;
    font-weight: 500;
    margin-bottom: 30px;
    line-height: 1.0;
}

.total-count {
    font-size: 5em;
    font-weight: 900;
    margin-bottom: 40px;
    line-height: 1.0;
    color: white; /* Pastikan warna tetap putih di background gelap */
}

.section-title {
    font-size: 1.2em;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
    color: rgba(255, 255, 255, 0.8); /* Warna lebih redup */
}

.top-route-item {
    font-size: 1.4em;
    font-weight: 700;
    margin-bottom: 15px;
}

.nocturnal-type {
    font-size: 3em;
    font-weight: 900;
    color: #FFD700; /* Warna kontras, misal kuning */
    margin-bottom: 15px;
}

.footer-text {
    font-size: 0.9em;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 50px;
    text-align: right;
}

/* Mengubah warna teks untuk bagian "Tipe Kamu" dan penjelasannya */
.type-section-title {
    font-size: 1.2em;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
    color: rgba(255, 255, 255, 0.8);
}

.type-description {
    font-size: 1.2em;
    font-weight: 500;
    color: white;
    margin-top: 10px;
}

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
# --- Akhir Bagian Styling ---

st.title("Web Scraping & Normalisasi Lintasan/Jadwal")
st.markdown("---")

# Text area untuk paste HTML
html_input = st.text_area("Paste HTML Riwayat Perjalanan Ferizy di sini:")

if st.button("Scrape & Generate Rekap"):
    if not html_input.strip():
        st.error("Silakan masukkan HTML terlebih dahulu!")
    else:
        try:
            soup = BeautifulSoup(html_input, "html.parser")
            
            # Ambil semua div yang memiliki class flex di dalamnya
            # Asumsi: Setiap elemen ini mewakili 1 kali perjalanan/jadwal
            div_elements = soup.find_all("div", {"data-v-28aa75d9": True})
            
            data = []
            for div in div_elements:
                # Ambil lintasan
                origin = div.find("span", class_="port-origin font-semibold")
                destination = div.find("span", class_="port-destination font-semibold")
                lintasan = ""
                if origin and destination:
                    # Ambil teks, pisahkan dengan strip() untuk menghilangkan whitespace
                    lintasan = f"{origin.get_text(strip=True)} - {destination.get_text(strip=True)}"
                
                # Ambil jadwal (span langsung di bawah div)
                jadwal_span = div.find("span", class_="", recursive=False)
                jadwal = ""
                if jadwal_span:
                    # Mengambil teks langsung dari span tanpa tag anak
                    jadwal = ''.join(jadwal_span.find_all(text=True, recursive=False)).strip()
                    # Hapus kata "Reguler" dan simbol "·"
                    jadwal = jadwal.replace("Reguler", "").replace("·", "").strip()
                
                data.append({
                    "Lintasan": lintasan,
                    "Jadwal": jadwal
                })
            
            # Buat DataFrame
            df = pd.DataFrame(data)
            
            # Normalisasi: hapus row dengan jadwal kosong atau lintasan kosong
            df = df[(df["Jadwal"] != "") & (df["Lintasan"] != "")].reset_index(drop=True)
            
            if not df.empty:
                
                # --- Statistik dan Rekapitulasi ---
                
                # 1. Hitung Total Perjalanan (Total baris setelah normalisasi)
                total_perjalanan = len(df)
                
                # 2. Hitung Top 3 Lintasan
                top_lintasan = df["Lintasan"].value_counts().nlargest(3)
                
                # 3. Klasifikasi Tipe (Sederhana: berdasarkan jam keberangkatan)
                
                # Pisahkan Jadwal menjadi Tanggal & Jam
                def split_date_time(jadwal):
                    # Mencari pola YYYY-MM-DD HH:MM
                    match = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})", jadwal)
                    if match:
                        return pd.Series([match.group(1), match.group(2)])
                    else:
                        return pd.Series(["", ""]) # Kembalikan string kosong jika tidak cocok
                
                df[["Tanggal", "Jam"]] = df["Jadwal"].apply(split_date_time)
                df["Jam_Keberangkatan"] = pd.to_datetime(df["Jam"], format='%H:%M', errors='coerce').dt.hour
                
                # Menentukan Tipe
                # Asumsi: Malam (Nocturnal) = Jam 22:00 - 04:00
                nocturnal_count = df[(df["Jam_Keberangkatan"] >= 22) | (df["Jam_Keberangkatan"] <= 4)].shape[0]
                
                # Tentukan Tipe berdasarkan mayoritas (lebih dari 50% di kategori malam)
                if nocturnal_count / total_perjalanan > 0.5:
                    tipe_kamu = "Nokturnal"
                    deskripsi_tipe = "Kamu suka bepergian di malam hari (22:00 - 04:00)"
                else:
                    tipe_kamu = "Diurnal"
                    deskripsi_tipe = "Kamu suka bepergian di siang/sore hari (05:00 - 21:00)"

                # --- Tampilkan Hasil Rekap dalam Bentuk Visual (Mirip Gambar Asli) ---
                st.markdown("## ✨ Rekap Ferizy Journey 2025 Anda")
                
                # Container Rekap
                st.markdown('<div class="ferizy-container">', unsafe_allow_html=True)
                
                st.markdown('<p class="ferizy-header">ferizy</p>', unsafe_allow_html=True)
                st.markdown('<p class="ferizy-subheader">JOURNEY 2025</p>', unsafe_allow_html=True)
                
                st.markdown(f'Tahun ini kamu udah nyebrang sama ferizy sebanyak')
                st.markdown(f'<p class="total-count">{total_perjalanan} Kali</p>', unsafe_allow_html=True)
                
                # Tampilkan Top Lintasan
                st.markdown('<p class="section-title">TOP LINTASANMU</p>', unsafe_allow_html=True)
                
                for i, (lintasan, count) in enumerate(top_lintasan.items()):
                    st.markdown(f'<p class="top-route-item">{i+1}. {lintasan} : {count} Kali</p>', unsafe_allow_html=True)

                # Tampilkan Tipe
                st.markdown('<p class="type-section-title">Tipe Kamu</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="nocturnal-type">{tipe_kamu.upper()}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="type-description">{deskripsi_tipe}</p>', unsafe_allow_html=True)

                st.markdown('<p class="footer-text">https://s.id/FerizyJourney</p>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                # --- Tampilkan Data Mentah dan Download CSV (Seperti Kode Awal) ---
                
                df.drop(columns=["Jadwal", "Jam_Keberangkatan"], inplace=True)
                
                st.write(f"Ditemukan {total_perjalanan} jadwal setelah normalisasi & pemisahan Tanggal/Jam")
                st.dataframe(df)
                
                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV Data Perjalanan",
                    data=csv,
                    file_name="jadwal_normalized.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Tidak ditemukan data jadwal yang valid setelah normalisasi.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
