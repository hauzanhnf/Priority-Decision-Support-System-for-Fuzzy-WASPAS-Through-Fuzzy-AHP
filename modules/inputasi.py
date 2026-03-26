import streamlit as st
import pandas as pd

tfn_scale = {
    1: (1,1,1),
    2: (1,2,4),
    3: (1,3,5),
    4: (2,4,6),
    5: (3,5,7),
    6: (4,6,8),
    7: (5,7,9)
}

def to_tfn(x):
    if isinstance(x,pd.Series):
        x=x.iloc[0]
    if pd.isna(x):
        return (1,1,1)
    return tfn_scale.get(int(x),(1,1,1))

def normalize_fuzzy(matrix,criteria):
    norm={}
    for c in criteria:
        max_u=max(matrix[a][c][2] for a in matrix)
        for a in matrix:
            l,m,u=matrix[a][c]
            norm.setdefault(a,{})[c]=(l/max_u,m/max_u,u/max_u)
    return norm


def fuzzy_wsm(norm_matrix,weights):
    scores={}
    for a in norm_matrix:
        l=m=u=0
        for c,w in weights.items():
            nl,nm,nu=norm_matrix[a][c]
            l+=nl*w
            m+=nm*w
            u+=nu*w
        scores[a]=(l,m,u)
    return scores


def fuzzy_wpm(norm_matrix,weights):
    scores={}
    for a in norm_matrix:
        l=m=u=1
        for c,w in weights.items():
            nl,nm,nu=norm_matrix[a][c]
            l*=nl**w
            m*=nm**w
            u*=nu**w
        scores[a]=(l,m,u)
    return scores

def fuzzy_waspas(wsm,wpm,lambda_val=0.5):
    final={}
    for a in wsm:
        l=lambda_val*wsm[a][0]+(1-lambda_val)*wpm[a][0]
        m=lambda_val*wsm[a][1]+(1-lambda_val)*wpm[a][1]
        u=lambda_val*wsm[a][2]+(1-lambda_val)*wpm[a][2]
        final[a]=(l,m,u)
    return final

def defuzzify(tfn):
    return (tfn[0]+tfn[1]+tfn[2])/3


# HALAMAN INPUTASI
def page_inputasi():

    st.title("✍️ Input Data Segmentasi Kemiskinan")
    st.write("Silakan isi data keluarga")


    if 'data_proses' not in st.session_state:
        st.error("Jalankan Segmentasi dulu")
        return


    data_proses=st.session_state['data_proses']


# BOBOT GLOBAL
    global_weights={

    'Frekuensi Makan Per Hari':0.16667,
    'Frekuensi Makan Daging Susu Ayam':0.07693,
    'Frekuensi Beli Pakaian':0.03189,

    'Pendapatan':0.21891,
    'Pendidikan':0.14433,
    'Simpanan':0.09154,
    'Akses Berobat':0.06236,

    'Sumber Penerangan':0.02605,
    'Bahan Bakar Memasak':0.04135,
    'Sumber Air Minum':0.06563,

    'Fasilitas BAB':0.03313,
    'Jenis Lantai':0.02048,
    'Luas Lantai':0.01297,
    'Jenis Dinding':0.00775
    }


# DAFTAR KECAMATAN
    daftar_kecamatan=[
    "Babadan","Badegan","Balong","Bungkal","Jambon",
    "Jenangan","Jetis","Kauman","Mlarak","Ngebel",
    "Ngrayun","Ponorogo","Pudak","Pulung","Sambit",
    "Sampung","Sawoo","Siman","Slahung","Sooko","Sukorejo"
    ]


# FORM INPUT
    with st.form("input_form"):
        kepala_keluarga=st.text_input("Nama Kepala Keluarga")
        kecamatan=st.selectbox("Kecamatan",sorted(daftar_kecamatan))
        desa=st.text_input("Desa/Kelurahan")
        frekuensi_makan=st.number_input("Frekuensi Makan per Hari",0,5,3)
        bisa_berobat=st.radio("Bisa Berobat?",["Ya","Tidak"])
        pendapatan=st.number_input("Pendapatan Bulanan",0)
        sumber_penerangan=st.selectbox("Sumber Penerangan",[
        'Listrik Pribadi s/d 900 Watt',
        'Listrik Pribadi > 900 Watt',
        'Non-Listrik',
        'Listrik Bersama',
        'Genset/solar cell'
        ])
        bahan_bakar=st.selectbox("Bahan Bakar Memasak",[
        'Listrik/Gas',
        'Minyak Tanah',
        'Arang/Kayu',
        'Lainnya'
        ])
        fasilitas_bab=st.selectbox("Fasilitas BAB",[
        'Ya, dengan Septic Tank',
        'Ya, tanpa Septic Tank',
        'Tidak, Jamban Umum/Bersama',
        'Lainnya'
        ])
        frek_makan_daging=st.number_input("Frekuensi Makan Daging Susu Ayam",0,21,1)
        luas_lantai=st.number_input("Luas Lantai",0)
        jenis_dinding=st.selectbox("Jenis Dinding",[
        'Tembok','Seng','Lainnya','Kayu/Papan','Bambu'
        ])
        sumber_air_minum=st.selectbox("Sumber Air",[
        'Ledeng/PAM','Air Kemasan/Isi Ulang',
        'Sumur Bor','Sumur Terlindung',
        'Sumur Tidak Terlindung',
        'Air Permukaan (Sungai, Danau, dll)',
        'Air Hujan','Lainnya'
        ])
        memiliki_simpanan=st.radio("Memiliki Simpanan?",["Ya","Tidak"])
        jenis_lantai=st.selectbox("Jenis Lantai",[
        'Keramik/Granit/Marmer/Ubin/Tegel/Teraso',
        'Semen','Lainnya','Kayu/Papan','Bambu','Tanah'
        ])
        frek_beli_pakaian=st.number_input("Beli Pakaian per Tahun",0,20,1)
        pendidikan=st.selectbox("Pendidikan",[
        'Tidak/belum sekolah',
        'Tidak tamat SD/sederajat',
        'Siswa SD/sederajat',
        'Tamat SD/sederajat',
        'Siswa SMP/sederajat',
        'Tamat SMP/sederajat',
        'Siswa SMA/sederajat',
        'Tamat SMA/sederajat',
        'Mahasiswa Perguruan Tinggi',
        'Tamat Perguruan Tinggi'
        ])

        submitted=st.form_submit_button("Proses")


# PROSES
    if submitted:
        try:
            data_baru={
            'Frekuensi Makan Per Hari':frekuensi_makan,
            'Frekuensi Makan Daging Susu Ayam':2 if frek_makan_daging<=1 else 1,
            'Frekuensi Beli Pakaian':2 if frek_beli_pakaian<=1 else 1,
            'Pendapatan':2 if pendapatan<=600000 else 1,
            'Pendidikan':{
            'Tidak/belum sekolah':5,
            'Tidak tamat SD/sederajat':5,
            'Siswa SD/sederajat':4,
            'Tamat SD/sederajat':4,
            'Siswa SMP/sederajat':3,
            'Tamat SMP/sederajat':3,
            'Siswa SMA/sederajat':2,
            'Tamat SMA/sederajat':2,
            'Mahasiswa Perguruan Tinggi':1,
            'Tamat Perguruan Tinggi':1
            }[pendidikan],
            'Simpanan':1 if memiliki_simpanan=="Ya" else 2,
            'Akses Berobat':1 if bisa_berobat=="Ya" else 2,
            'Sumber Penerangan':{
            'Listrik Pribadi s/d 900 Watt':1,
            'Listrik Pribadi > 900 Watt':1,
            'Non-Listrik':2,
            'Listrik Bersama':2,
            'Genset/solar cell':2
            }[sumber_penerangan],
            'Bahan Bakar Memasak':{
            'Listrik/Gas':1,
            'Minyak Tanah':2,
            'Arang/Kayu':3,
            'Lainnya':2
            }[bahan_bakar],
            'Sumber Air Minum':{
            'Ledeng/PAM':1,
            'Air Kemasan/Isi Ulang':1,
            'Sumur Bor':1,
            'Sumur Terlindung':1,
            'Sumur Tidak Terlindung':2,
            'Air Permukaan (Sungai, Danau, dll)':3,
            'Air Hujan':4,
            'Lainnya':3
            }[sumber_air_minum],
            'Fasilitas BAB':{
            'Ya, dengan Septic Tank':1,
            'Ya, tanpa Septic Tank':2,
            'Tidak, Jamban Umum/Bersama':3,
            'Lainnya':2
            }[fasilitas_bab],
            'Jenis Lantai':{
            'Keramik/Granit/Marmer/Ubin/Tegel/Teraso':1,
            'Semen':2,
            'Lainnya':3,
            'Kayu/Papan':3,
            'Bambu':4,
            'Tanah':5
            }[jenis_lantai],
            'Luas Lantai':2 if luas_lantai<=8 else 1,
            'Jenis Dinding':{
            'Tembok':1,
            'Seng':2,
            'Lainnya':2,
            'Kayu/Papan':3,
            'Bambu':4
            }[jenis_dinding]
            }

            criteria_cols=list(global_weights.keys())

            df_history = data_proses[criteria_cols].copy()
            df_new = pd.DataFrame([data_baru])
            df_combined = df_history.copy()
            df_combined.loc["INPUT"] = df_new.iloc[0]

            fuzzy_matrix={
            i:{c:to_tfn(df_combined.loc[i,c]) for c in criteria_cols}
            for i in df_combined.index
            }


            norm_matrix=normalize_fuzzy(fuzzy_matrix,criteria_cols)
            wsm=fuzzy_wsm(norm_matrix,global_weights)
            wpm=fuzzy_wpm(norm_matrix,global_weights)
            final=fuzzy_waspas(wsm,wpm)

            score_new=defuzzify(final["INPUT"])
            scores=pd.Series([defuzzify(final[k]) for k in final])

            q1=scores.quantile(0.90)
            q2=scores.quantile(0.70)
            q3=scores.quantile(0.40)

            if score_new>=q1:
                cluster=1
                desc="Sangat Prioritas"

            elif score_new>=q2:

                cluster=2
                desc="Prioritas"

            elif score_new>=q3:

                cluster=3
                desc="Cukup Prioritas"

            else:

                cluster=4
                desc="Bukan Prioritas"


 
            st.success("Perhitungan Selesai")
            st.metric("Skor WASPAS",round(score_new,5))
            st.write("Desil:",cluster,"-",desc)

            # RINCIAN DATA INPUT
            st.markdown("---")
            st.markdown("### 📋 Rincian Data")

            display_data = {
            "Kepala Keluarga":kepala_keluarga,
            "Kecamatan":kecamatan,
            "Desa/Kelurahan":desa,
            "Frekuensi Makan":f"{frekuensi_makan} kali/hari",
            "Akses Berobat ke Puskesmas":
            "Bisa" if bisa_berobat=="Ya" else "Tidak Bisa",
            "Pendapatan Bulanan":
            f"Rp {pendapatan:,.0f}".replace(",", "."),
            "Sumber Penerangan":sumber_penerangan,
            "Bahan Bakar Memasak":bahan_bakar,
            "Fasilitas BAB":fasilitas_bab,
            "Konsumsi Daging/Susu":
            f"{frek_makan_daging} kali/minggu",
            "Luas Lantai":f"{luas_lantai} m²",
            "Jenis Dinding":jenis_dinding,
            "Sumber Air Minum":sumber_air_minum,
            "Simpanan":memiliki_simpanan,
            "Jenis Lantai":jenis_lantai,
            "Beli Pakaian Baru":
            f"{frek_beli_pakaian} kali/tahun",
            "Pendidikan Terakhir":pendidikan
            }


            for label,value in display_data.items():
                col_kiri,col_kanan=st.columns([2,3])
                with col_kiri:
                    st.markdown(
                    f"<span style='color:grey; font-weight:500'>{label}</span>",
                    unsafe_allow_html=True
                    )
                with col_kanan:
                    st.write(f": **{value}**")

        except Exception as e:
            st.error(e)