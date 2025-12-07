import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

st.title("Web Scraping Lintasan & Jadwal dari HTML")

# Text area untuk paste HTML
html_input = st.text_area("Paste HTML di sini:")

if st.button("Scrape"):
    if not html_input.strip():
        st.error("Silakan masukkan HTML terlebih dahulu!")
    else:
        try:
            soup = BeautifulSoup(html_input, "html.parser")
            
            # Ambil semua elemen class 'flex'
            flex_elements = soup.find_all(class_="flex")
            
            if not flex_elements:
                st.warning("Tidak ditemukan elemen dengan class 'flex'.")
            else:
                data = []
                for elem in flex_elements:
                    # Ambil port-origin dan port-destination
                    origin = elem.find(class_="port-origin font-semibold")
                    destination = elem.find(class_="port-destination font-semibold")
                    lintasan = ""
                    if origin and destination:
                        lintasan = f"{origin.get_text(strip=True)} - {destination.get_text(strip=True)}"
                    
                    # Ambil jadwal (span dengan attribute tertentu)
                    jadwal_elem = elem.find("span", {"data-v-28aa75d9": True})
                    jadwal = jadwal_elem.get_text(strip=True) if jadwal_elem else ""
                    
                    data.append({
                        "Lintasan": lintasan,
                        "Jadwal": jadwal
                    })
                
                df = pd.DataFrame(data)
                
                st.write(f"Ditemukan {len(data)} jadwal")
                st.dataframe(df)
                
                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="jadwal.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
