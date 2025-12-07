import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re
from PIL import Image, ImageDraw, ImageFont
import io 

st.set_page_config(layout="centered")

st.title("Web Scraping & Generate Gambar Rekap Ferizy")
st.markdown("---")

# Text area untuk paste HTML
html_input = st.text_area("Paste HTML Riwayat Perjalanan Ferizy di sini:")

# GANTI NAMA FILE INI DENGAN NAMA FILE .JPG BACKGROUND ANDA YANG SEBENARNYA
BACKGROUND_IMAGE_PATH = "my_background.jpg" 
# Pastikan file .jpg ini ada di folder yang sama dengan script Streamlit Anda!

if st.button("Scrape & Generate Gambar Rekap"):
    if not html_input.strip():
        st.error("Silakan masukkan HTML terlebih dahulu!")
    else:
        try:
            # --- Bagian Scraping Data ---
            soup = BeautifulSoup(html_input, "html.parser")
            div_elements = soup.find_all("div", {"data-v-28aa75d9": True})
            
            data = []
            for div in div_elements:
                origin = div.find("span", class_="port-origin font-semibold")
                destination = div.find("span", class_="port-destination font-semibold")
                lintasan = ""
                if origin and destination:
                    lintasan = f"{origin.get_text(strip=True)} - {destination.get_text(strip=True)}"
                
                jadwal_span = div.find("span", class_="", recursive=False)
                jadwal = ""
                if jadwal_span:
                    jadwal = ''.join(jadwal_span.find_all(text=True, recursive=False)).strip()
                    jadwal = jadwal.replace("Reguler", "").replace("·", "").strip()
                # TIDAK ADA ELSE DI SINI UNTUK MENGHINDARI IndentationError
                
                data.append({"Lintasan": lintasan, "Jadwal": jadwal})
            
            df = pd.DataFrame(data)
            df = df[(df["Jadwal"] != "") & (df["Lintasan"] != "")].reset_index(drop=True)
            
            if not df.empty:
                # --- Statistik dan Rekapitulasi ---
                total_perjalanan = len(df)
                top_lintasan = df["Lintasan"].value_counts().nlargest(3)
                
                def split_date_time(jadwal):
                    match = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})", jadwal)
                    if match:
                        return pd.Series([match.group(1), match.group(2)])
                    else:
                        return pd.Series(["", ""])
                
                df[["Tanggal", "Jam"]] = df["Jadwal"].apply(split_date_time)
                df["Jam_Keberangkatan"] = pd.to_datetime(df["Jam"], format='%H:%M', errors='coerce').dt.hour
                
                nocturnal_count = df[(df["Jam_Keberangkatan"] >= 22) | (df["Jam_Keberangkatan"] <= 4)].shape
