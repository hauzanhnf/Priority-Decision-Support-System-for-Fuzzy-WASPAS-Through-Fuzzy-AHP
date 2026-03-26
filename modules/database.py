import streamlit as st
import pandas as pd

# Fungsi load data awal
@st.cache_data
def load_data():
    df = pd.read_excel("data/data_kemiskinan_bersih.xlsx")
    return df

# Halaman Database
def page_database():
    st.title("📁 Database Segmentasi Kemiskinan")
    df = load_data()

    if not df.empty:
        kolom_nama = st.selectbox("Pilih kolom untuk pencarian:", df.columns)
        input_nama = st.text_input("Masukkan kata kunci pencarian:")

        if input_nama:
            hasil = df[df[kolom_nama].astype(str).str.contains(input_nama, case=False, na=False)]
            st.subheader("📌 Hasil Pencarian")
            if not hasil.empty:
                st.success(f"{len(hasil)} data ditemukan.")
                st.dataframe(hasil)
            else:
                st.warning("Data tidak ditemukan.")
        else:
            st.subheader("📋 Pratinjau Seluruh Data")
            st.dataframe(df)
    else:
        st.warning("Data kosong atau gagal dimuat.")
