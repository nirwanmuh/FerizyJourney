import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

st.title("Web Scraping & Normalisasi Lintasan/Jadwal")

# Text area untuk paste HTML
html_input = st.text_area("Paste HTML di sini:")

if st.button("Scrape & Normalisasi"):
    if not html_input.strip():
        st.error("Silakan masukkan HTML terlebih dahulu!")
    else:
        try:
            soup = BeautifulSoup(html_input, "html.parser")
            
            # Ambil semua div yang memiliki class flex di dalamnya
            div_elements = soup.find_all("div", {"data-v-28aa75d9": True})
            
            data = []
            for div in div_elements:
                # Ambil lintasan
                origin = div.find("span", class_="port-origin font-semibold")
                destination = div.find("span", class_="port-destination font-semibold")
                lintasan = ""
                if origin and destination:
                    lintasan = f"{origin.get_text(strip=True)} - {destination.get_text(strip=True)}"
                
                # Ambil jadwal (span langsung di bawah div)
                jadwal_span = div.find("span", class_="", recursive=False)
                jadwal = ""
                if jadwal_span:
                    jadwal = ''.join(jadwal_span.find_all(text=True, recursive=False)).strip()
                    # Hapus kata "Reguler" dan simbol "·"
                    jadwal = jadwal.replace("Reguler", "").replace("·", "").strip()
                
                data.append({
                    "Lintasan": lintasan,
                    "Jadwal": jadwal
                })
            
            # Buat DataFrame
            df = pd.DataFrame(data)
            
            # Normalisasi: hapus row dengan jadwal kosong
            df = df[df["Jadwal"] != ""].reset_index(drop=True)
            
            if not df.empty:
                # Pisahkan Jadwal menjadi Tanggal & Jam
                def split_date_time(jadwal):
                    match = re.match(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})", jadwal)
                    if match:
                        return pd.Series([match.group(1), match.group(2)])
                    else:
                        return pd.Series([jadwal, ""])
                
                df[["Tanggal", "Jam"]] = df["Jadwal"].apply(split_date_time)
                df.drop(columns=["Jadwal"], inplace=True)
                
                st.write(f"Ditemukan {len(df)} jadwal setelah normalisasi & pemisahan Tanggal/Jam")
                st.dataframe(df)
                
                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="jadwal_normalized.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Tidak ditemukan data jadwal yang valid setelah normalisasi.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
