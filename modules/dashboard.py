import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import re

def prettify_column_name(col_name):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', col_name)

def page_dashboard():
    st.title("📊 Dashboard Segmentasi Kemiskinan Kabupaten Ponorogo")

    if 'data_proses' not in st.session_state:
        st.warning("Data hasil segmentasi belum tersedia. Silakan lakukan proses segmentasi terlebih dahulu.")
        return

    # ========================
    # Ambil data awal
    try:
        df_awal = pd.read_excel("data/data_kemiskinan_bersih.xlsx")
    except Exception as e:
        st.error(f"Gagal memuat data awal: {e}")
        return

    df_proses = st.session_state['data_proses']

    # Ambil kolom WASPAS, Rank, Cluster
    df_saw_summary = df_proses[['WASPAS', 'Rank', 'Cluster']].reset_index(drop=True)
    df_awal = df_awal.reset_index(drop=True)

    # Gabungkan data
    df = pd.concat([df_awal, df_saw_summary], axis=1)

    if df.empty:
        st.warning("Data gabungan kosong.")
        return

    # ========================
    # HITUNG CLUSTER DOMINAN PER KECAMATAN
    st.subheader("🗺️ Peta Sebaran Kemiskinan per Kecamatan di Ponorogo")


    # ========================
    # CALCULATE AVERAGE WASPAS PER KECAMATAN
    mean_saw = df.groupby('Kecamatan')['WASPAS'].mean().reset_index()
    mean_saw = mean_saw.sort_values('WASPAS', ascending=False)

    # Normalize kecamatan names to match shapefile
    mean_saw['Kecamatan'] = mean_saw['Kecamatan'].str.upper().str.strip()

    # ========================
    # LOAD SHAPEFILE
    try:
        gdf_kec = gpd.read_file("geodata/ponorogo_kecamatan_highres.shp")
    except Exception as e:
        st.error(f"Gagal memuat shapefile: {e}")

    # Normalize names in shapefile
    gdf_kec['ADM3_EN'] = gdf_kec['ADM3_EN'].str.upper().str.strip()

    # ========================
    # MERGE GEO DATA WITH WASPAS DATA
    gdf_map = gdf_kec.merge(
        mean_saw,
        left_on='ADM3_EN',
        right_on='Kecamatan',
        how='left'
    )

    # Ensure CRS is WGS84 (EPSG:4326) for Folium
    if gdf_map.crs is None or gdf_map.crs.to_epsg() != 4326:
        gdf_map = gdf_map.to_crs(epsg=4326)

    # ========================
    # CREATE COLOR SCALE (light = low, red = high)
    min_score = gdf_map['WASPAS'].min()
    max_score = gdf_map['WASPAS'].max()

    colormap = cm.linear.YlOrRd_09.scale(min_score, max_score)
    colormap.caption = "Rata-rata Skor WASPAS"

    # ========================
    # CREATE FOLIUM MAP
    m = folium.Map(
        location=[-7.87, 111.46],  # Center of Ponorogo
        zoom_start=10,
        tiles="cartodbpositron"
    )

    folium.GeoJson(
        gdf_map,
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["WASPAS"])
            if feature["properties"]["WASPAS"] is not None else "#cccccc",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["ADM3_EN", "WASPAS"],
            aliases=["Kecamatan", "Rata-rata WASPAS"],
            localize=True,
            sticky=True
        ),
    ).add_to(m)

    # Add the color legend
    colormap.add_to(m)

    # Display in Streamlit
    st_folium(m, width=700, height=500)
    # Checkbox visualisasi berdasarkan cluster
    use_cluster = st.checkbox("Tampilkan Visualisasi Berdasarkan Cluster", value=True)


    # Bar Chart Kolom Kategorikal / Ordinal
    st.subheader("📈 Frekuensi Data Berdasarkan Kolom")
    possible_cat_cols = [col for col in df.columns if df[col].dtype in ['object', 'category', 'float64', 'int64']]
    bar_col = st.selectbox("Pilih Kolom:", options=possible_cat_cols)

    if bar_col:
        if use_cluster and 'Cluster' in df.columns and bar_col != 'Cluster':
            freq_df = df.groupby(['Cluster', bar_col]).size().reset_index(name='Jumlah')
            fig = px.bar(freq_df, x=bar_col, y='Jumlah', color='Cluster', barmode='group',
                         title=f"Distribusi {bar_col} berdasarkan Cluster")
        else:
            freq_df = df[bar_col].value_counts().reset_index()
            freq_df.columns = [bar_col, 'Jumlah']
            fig = px.bar(freq_df, x=bar_col, y='Jumlah',
                         title=f"Distribusi {bar_col}")

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Lihat Data Tabel"):
            st.dataframe(freq_df)
            csv = freq_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="bar_chart_data.csv", mime="text/csv")

    # Distribusi Skor WASPAS
    if 'WASPAS' in df.columns:
        st.subheader("💰 Analisis Distribusi Skor WASPAS")

        tab1, tab2, tab3= st.tabs(["📊 Histogram", "📦 Box Plot", "🎻 Violin Plot"])

        with tab1:
            fig = px.histogram(df, x='WASPAS', nbins=30,
                               color='Cluster' if use_cluster else None,
                               title="Histogram Skor WASPAS")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = px.box(df, x='Cluster' if use_cluster else None, y='WASPAS',
                         color='Cluster' if use_cluster else None,
                         title="Box Plot Skor WASPAS")
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = px.violin(df, x='Cluster' if use_cluster else None, y='WASPAS',
                            color='Cluster' if use_cluster else None, box=True, points='all',
                            title="Violin Plot Skor WASPAS")
            st.plotly_chart(fig, use_container_width=True)


    # Proporsi Keluarga per Cluster
    if 'Cluster' in df.columns:
        st.subheader("🚨 Proporsi Keluarga per Cluster")
    
        # Hitung jumlah & proporsi
        cluster_count = df['Cluster'].value_counts().sort_index()
        cluster_prop = df['Cluster'].value_counts(normalize=True).sort_index() * 100
    
        # DataFrame
        df_cluster_prop = pd.DataFrame({
            'Cluster': cluster_count.index,
            'Jumlah Warga': cluster_count.values,
            'Proporsi (%)': cluster_prop.values.round(2)
        })
    
        # Tabel
        st.dataframe(df_cluster_prop, use_container_width=True)


    # Analisis per Kecamatan
    if 'Kecamatan' in df.columns and 'WASPAS' in df.columns:
        st.subheader("📌 Analisis Skor WASPAS per Kecamatan")
        fig_box = px.box(df, x='Kecamatan', y='WASPAS', points='all',
                         color='Cluster' if use_cluster else None,
                         title="Sebaran Skor WASPAS per Kecamatan")
        fig_box.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_box, use_container_width=True)

        # Rata-rata per kecamatan
        mean_saw = df.groupby('Kecamatan')['WASPAS'].mean().reset_index()
        mean_saw = mean_saw.sort_values('WASPAS', ascending=False)
        st.markdown("#### 🏆 Kecamatan dengan Rata-rata Skor WASPAS Tertinggi & Terendah")
        col1, col2 = st.columns(2)
        col1.metric("📈 Tertinggi", value=mean_saw.iloc[0]['Kecamatan'], delta=f"{mean_saw.iloc[0]['WASPAS']:.2f}")
        col2.metric("📉 Terendah", value=mean_saw.iloc[-1]['Kecamatan'], delta=f"{mean_saw.iloc[-1]['WASPAS']:.2f}")

        fig_mean_saw = px.bar(mean_saw, x='Kecamatan', y='WASPAS', color='WASPAS',
                              color_continuous_scale='Reds',
                              title="Rata-rata Skor WASPAS per Kecamatan")
        fig_mean_saw.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_mean_saw, use_container_width=True)

        # ============================================================
        # BAGIAN YANG DIUBAH: Proporsi cluster per kecamatan (GABUNGAN)
        # ============================================================
        st.subheader("🚨 Proporsi Keluarga per Cluster di Tiap Kecamatan")
        
        # 1. Siapkan Data
        cluster_counts = df.groupby(['Kecamatan', 'Cluster']).size().reset_index(name='Jumlah')
        total_counts = df.groupby('Kecamatan').size().reset_index(name='Total')
        merged = pd.merge(cluster_counts, total_counts, on='Kecamatan')
        merged['Proporsi'] = merged['Jumlah'] / merged['Total']

        # Pastikan Cluster bersifat kategorikal agar urutan warna benar/diskrit
        merged['Cluster'] = merged['Cluster'].astype(str) 

        # 2. Definisi Warna Custom (Agar intuitif: Merah=Miskin, Hijau=Mampu)
        # Sesuaikan key string '1', '2' dst dengan data Anda
        color_map = {
            '1': '#d62728',  # Merah (Prioritas 1)
            '2': '#ff7f0e',  # Oranye (Prioritas 2)
            '3': '#fecb52',  # Kuning (Prioritas 3)
            '4': '#2ca02c'   # Hijau (Prioritas 4)
        }

        # 3. Buat Stacked Bar Chart Gabungan
        fig_combined = px.bar(
            merged, 
            x='Kecamatan', 
            y='Proporsi', 
            color='Cluster',
            title="Komposisi Cluster Kemiskinan per Kecamatan",
            color_discrete_map=color_map, # Gunakan warna custom
            hover_data={'Proporsi':':.1%', 'Jumlah':True, 'Total':True}, # Tooltip informatif
            category_orders={"Cluster": ["1", "2", "3", "4"]} # Urutan legenda
        )

        # 4. Update Layout
        fig_combined.update_layout(
            xaxis_tickangle=-45, 
            yaxis_tickformat='.0%', # Format sumbu Y jadi persen
            yaxis_title="Proporsi (%)",
            legend_title_text="Kategori Cluster",
            barmode='stack' # Mode tumpuk
        )

        # 5. Tampilkan
        st.plotly_chart(fig_combined, use_container_width=True)

        # Tampilkan Data Tabel di bawahnya (Pivot agar mudah dibaca)
        with st.expander("📄 Lihat Data Detail Proporsi"):
            pivot_data = merged.pivot(index='Kecamatan', columns='Cluster', values='Proporsi').fillna(0)
            st.dataframe(pivot_data.style.format("{:.1%}"))


        # Top 10 Kecamatan terpolarisasi
        st.subheader("🧭 Top 10 Kecamatan Paling Terpolarisasi")
        cluster_props = df.groupby(['Kecamatan','Cluster']).size().unstack(fill_value=0)
        cluster_props = cluster_props.div(cluster_props.sum(axis=1), axis=0)
        min_cl, max_cl = cluster_props.columns.min(), cluster_props.columns.max()
        cluster_props['Polarization'] = abs(cluster_props[max_cl] - cluster_props[min_cl])
        top10_polar = cluster_props['Polarization'].sort_values(ascending=False).head(10).reset_index()
        st.dataframe(top10_polar.rename(columns={'Polarization':'Selisih Proporsi'}))


        # Fungsi interpretasi proporsi
        def interpretasi_proporsi(prop_series, var_name, mapping=None):
            if mapping:
                prop_series.index = prop_series.index.map(mapping)

            max_val = prop_series.idxmax()
            max_prop = prop_series.max()

            interpretasi = f"Mayoritas responden untuk variabel **{var_name}** berada pada kategori **{max_val}** dengan proporsi sebesar **{max_prop:.1f}%**."

            if len(prop_series) > 1:
                sorted_props = prop_series.sort_values(ascending=False)
                second_val = sorted_props.index[1]
                second_prop = sorted_props.iloc[1]
                if second_prop > 20:
                    interpretasi += f" Kategori berikutnya adalah **{second_val}** dengan proporsi sebesar **{second_prop:.1f}%**."

            return interpretasi

        st.markdown("## 📊 Proporsi Variabel Kemiskinan Berdasarkan Cluster")
        indikator_cols = [
            'Frekuensi Makan Per Hari',
            'Akses Berobat',
            'Pendapatan',
            'Sumber Penerangan',
            'Bahan Bakar Memasak',
            'Fasilitas BAB',
            'Frekuensi Makan Daging Susu Ayam',
            'Luas Lantai',
            'Jenis Dinding',
            'Sumber Air Minum',
            'Simpanan',
            'Jenis Lantai',
            'Frekuensi Beli Pakaian',
            'Pendidikan'
        ]

        # Label mapping
        label_mapping = {
            'Pendidikan': {
                1: 'Perguruan Tinggi',
                2: 'SMA',
                3: 'SMP',
                4: 'SD',
                5: 'Tidak Sekolah'},
            'Fasilitas BAB': {
                1: 'Ya, dengan Septic Tank',
                2: 'Ya, tanpa Septic Tank',
                3: 'Tidak, Jamban Umum/Bersama'},
            'Sumber Penerangan': {
                1: 'Listrik PLN',
                2: 'Listrik Non-PLN'},
            'Bahan Bakar Memasak': {
                1: 'Listrik/Gas',
                2: 'Minyak Tanah',
                3: 'Kayu/Arang/Lainnya'},
            'Jenis Lantai': {
                1: 'Keramik/Granit/Marmer/Ubin/Tegel/Teraso',
                2: 'Semen',
                3: 'Kayu/Papan',
                4: 'Bambu',
                5: 'Tanah'},
            'Jenis Dinding': {
                1: 'Tembok',
                2: 'Seng',
                3: 'Kayu/Papan',
                4: 'Bambu'},
            'Sumber Air Minum': {
                1: 'Ledeng/PAM/Kemasan/Sumur Bor/Terlindung',
                2: 'Sumur Tidak Terlindung',
                3: 'Air Permukaan/Lainnya',
                4: 'Air Hujan'},
            'Simpanan': {1: 'Ya', 2: 'Tidak'},
            'Akses Berobat': {1: 'Ya', 2: 'Tidak'},
            'Frekuensi Makan Per Hari': {
                1: '1 Kali',
                2: '2 Kali',
                3: '3 Kali atau Lebih'},
            'Frekuensi Makan Daging Susu Ayam': {
                1: '1 Kali/Jarang',
                2: '2 Kali/Kadang',
                3: '3 Kali atau Lebih/Sering'},
            'Frekuensi Beli Pakaian': {
                0: '<1x/tahun',
                1: '1x/tahun',
                2: '2x/tahun',
                3: '≥3x/tahun'},
            'Pendapatan': {1: '>600k', 2: '<=600k'},
            'Luas Lantai': {1: '>8m2', 2: '<8m2'}
        }

        # Buat tab untuk tiap cluster
        tabs = st.tabs([f"Cluster {i}" for i in sorted(df_proses['Cluster'].unique())])

        # Loop setiap cluster
        for i, cluster_id in enumerate(sorted(df_proses['Cluster'].unique())):
            with tabs[i]:
                st.markdown(f"### 🔍 Distribusi Variabel di Cluster {cluster_id}")
                df_cluster = df_proses[df_proses['Cluster'] == cluster_id]

                for col in indikator_cols:
                    # Nama kolom tampil (pakai spasi)
                    display_col_name = prettify_column_name(col)
                    st.markdown(f"**{display_col_name}**")
                    
                    # Hitung jumlah & proporsi
                    count = df_cluster[col].value_counts().sort_index()
                    prop = df_cluster[col].value_counts(normalize=True).sort_index() * 100
                    
                    # Mapping label (jika tersedia)
                    if col in label_mapping:
                        count.index = count.index.map(label_mapping[col])
                        prop.index = prop.index.map(label_mapping[col])
                    
                    # Buat dataframe
                    df_prop = pd.DataFrame({
                        'Kategori': count.index,
                        'Jumlah': count.values,
                        'Proporsi (%)': prop.values.round(2)
                    })
                    
                    # Tampilkan tabel
                    st.dataframe(df_prop, use_container_width=True)
                    
                    # Interpretasi otomatis (pakai proporsi asli)
                    interpretasi = interpretasi_proporsi(
                        df_cluster[col].value_counts(normalize=True).sort_index() * 100,
                        col,
                        label_mapping.get(col)
                    )
                    st.markdown(f"> {interpretasi}")
