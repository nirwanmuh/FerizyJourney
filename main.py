import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Web Scraping Class='flex'")

# Input URL
url = st.text_input("Masukkan URL:")

if st.button("Scrape"):
    if not url:
        st.error("Silakan masukkan URL terlebih dahulu!")
    else:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                st.error(f"Gagal mengakses URL. Status code: {response.status_code}")
            else:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Ambil semua elemen class 'flex'
                flex_elements = soup.find_all(class_="flex")
                
                if not flex_elements:
                    st.warning("Tidak ditemukan elemen dengan class 'flex'.")
                else:
                    # Simpan hasil ke DataFrame
                    data = []
                    for i, elem in enumerate(flex_elements, 1):
                        data.append({
                            "No": i,
                            "Teks": elem.get_text(strip=True),
                            "HTML": str(elem)
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # Tampilkan di Streamlit
                    st.write(f"Ditemukan {len(flex_elements)} elemen dengan class 'flex'")
                    st.dataframe(df)
                    
                    # Download sebagai CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="flex_elements.csv",
                        mime="text/csv"
                    )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
