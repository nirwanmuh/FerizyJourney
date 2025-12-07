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
                
                nocturnal_count = df[(df["Jam_Keberangkatan"] >= 22) | (df["Jam_Keberangkatan"] <= 4)].shape[0]
                
                if total_perjalanan > 0 and (nocturnal_count / total_perjalanan) > 0.5:
                    tipe_kamu = "Nokturnal"
                    deskripsi_tipe = "Kamu suka bepergian di malam hari"
                else:
                    tipe_kamu = "Diurnal"
                    deskripsi_tipe = "Kamu suka bepergian di siang/sore hari"

                # --- BAGIAN GENERASI GAMBAR (Memuat JPG & Menempelkan Teks) ---
                
                img_width = 720
                img_height = 1280 
                image = None
                
                try:
                    # 1. Muat Gambar Background JPG
                    background_img = Image.open(BACKGROUND_IMAGE_PATH).convert("RGB") 
                    
                    # 2. Resize gambar agar sesuai dengan ukuran output
                    image = background_img.resize((img_width, img_height))
                    
                    # 3. Tambahkan overlay (OPSIONAL, jika teks sulit dibaca di background terang)
                    # Jika background Anda sudah gelap, Anda bisa menghapus 3 baris di bawah ini
                    overlay = Image.new('RGBA', image.size, (0, 0, 0, 150)) # Overlay hitam 60% transparan
                    image.paste(overlay, (0, 0), overlay)
                    
                    st.success(f"Berhasil memuat gambar background: {BACKGROUND_IMAGE_PATH}. Teks akan ditempelkan di atasnya.")
                    
                except FileNotFoundError:
                    st.error(f"File background '{BACKGROUND_IMAGE_PATH}' TIDAK DITEMUKAN. Tidak dapat membuat gambar.")
                    return # Hentikan proses jika gambar tidak ditemukan

                draw = ImageDraw.Draw(image)

                # Load Font (Pastikan file font tersedia jika tidak ingin menggunakan default)
                # Jika font tidak ditemukan, kode akan fallback ke font default Pillow
                try:
                    font_path_bold = "arialbd.ttf"
                    font_path_regular = "arial.ttf" 
                    
                    font_ferizy_logo = ImageFont.truetype(font_path_bold, 80)
                    font_journey = ImageFont.truetype(font_path_regular, 40)
                    font_header_medium = ImageFont.truetype(font_path_regular, 30)
                    font_total_count = ImageFont.truetype(font_path_bold, 100)
                    font_section_title = ImageFont.truetype(font_path_regular, 35)
                    font_top_item = ImageFont.truetype(font_path_regular, 40)
                    font_type_large = ImageFont.truetype(font_path_bold, 80)
                    font_type_desc = ImageFont.truetype(font_path_regular, 35)
                    font_footer = ImageFont.truetype(font_path_regular, 25)

                except Exception as e:
                    font_ferizy_logo = font_journey = font_header_medium = font_total_count = font_section_title = font_top_item = font_type_large = font_type_desc = font_footer = ImageFont.load_default()

                text_color_white = (255, 255, 255)
                text_color_grey = (200, 200, 200)
                text_color_yellow = (255, 215, 0) 

                # Posisi Teks (Pengaturan posisi di bawah ini akan menempelkan teks di atas gambar)
                y_offset = 60
                left_margin = 60

                # ferizy logo
                draw.text((left_margin, y_offset), "ferizy", fill=text_color_white, font=font_ferizy_logo)
                y_offset += 85 
                draw.text((left_margin, y_offset), "JOURNEY 2025", fill=text_color_white, font=font_journey)
                y_offset += 120

                # "Tahun ini kamu udah nyebrang..."
                draw.text((left_margin, y_offset), "Tahun ini kamu udah nyebrang", fill=text_color_white, font=font_header_medium)
                y_offset += 40
                draw.text((left_margin, y_offset), "sama ferizy sebanyak", fill=text_color_white, font=font_header_medium)
                y_offset += 80

                # Jumlah Total Perjalanan
                draw.text((left_margin, y_offset), f"{total_perjalanan} Kali", fill=text_color_white, font=font_total_count)
                y_offset += 150

                # TOP LINTASANMU
                draw.text((left_margin, y_offset), "TOP LINTASANMU", fill=text_color_grey, font=font_section_title)
                y_offset += 50
                for i, (lintasan, count) in enumerate(top_lintasan.items()):
                    draw.text((left_margin, y_offset), f"{i+1}. {lintasan} : {count} Kali", fill=text_color_white, font=font_top_item)
                    y_offset += 55
                y_offset += 50

                # Tipe Kamu
                draw.text((left_margin, y_offset), "Tipe Kamu", fill=text_color_grey, font=font_section_title)
                y_offset += 50
                draw.text((left_margin, y_offset), tipe_kamu.upper(), fill=text_color_yellow, font=font_type_large)
                y_offset += 80
                draw.text((left_margin, y_offset), deskripsi_tipe, fill=text_color_white, font=font_type_desc)
                
                # Footer
                draw.text((img_width - left_margin - 300, img_height - 60), "https://s.id/FerizyJourney", fill=text_color_grey, font=font_footer)


                # Simpan gambar ke buffer dan tampilkan
                img_buffer = io.BytesIO()
                image.save(img_buffer, format="PNG") 
                img_buffer.seek(0) 

                st.markdown("## ✨ Rekap Ferizy Journey 2025 Anda (Gambar)")
                st.image(img_buffer, caption="Rekap Perjalanan Ferizy Anda", use_column_width=True)

                # Tambahkan tombol download gambar
                st.download_button(
                    label="Download Gambar Rekap",
                    data=img_buffer,
                    file_name="ferizy_journey_rekap.png",
                    mime="image/png"
                )

                st.markdown("---")
                # --- Tampilkan Data Mentah ---
                
                df.drop(columns=["Jadwal", "Jam_Keberangkatan"], inplace=True)
                
                st.write(f"Ditemukan {total_perjalanan} jadwal setelah normalisasi & pemisahan Tanggal/Jam")
                st.dataframe(df)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV Data Perjalanan",
                    data=csv,
                    file_name="jadwal_normalized.csv",
                    mime="text/csv"
                )
            else:
