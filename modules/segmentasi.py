import streamlit as st
import pandas as pd

tfn_scale = {

    1:(1,1,1),
    2:(1,2,4),
    3:(1,3,5),
    4:(2,4,6),
    5:(3,5,7),
    6:(4,6,8),
    7:(5,7,9)
}

def to_tfn(x):
    return tfn_scale.get(int(x),(1,1,1))

# Normalisasi Fuzzy
def normalize_fuzzy(matrix,criteria):
    norm={}
    for c in criteria:
        max_u=max(matrix[a][c][2] for a in matrix)
        for a in matrix:
            l,m,u=matrix[a][c]
            norm.setdefault(a,{})[c]=(
                l/max_u,
                m/max_u,
                u/max_u
            )
    return norm


# Fuzzy WSM
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


# Fuzzy WPM
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


# Fuzzy WASPAS
def fuzzy_waspas(wsm,wpm,lambda_val):
    final={}
    for a in wsm:
        l=lambda_val*wsm[a][0]+(1-lambda_val)*wpm[a][0]
        m=lambda_val*wsm[a][1]+(1-lambda_val)*wpm[a][1]
        u=lambda_val*wsm[a][2]+(1-lambda_val)*wpm[a][2]
        final[a]=(l,m,u)
    return final

# Defuzzifikasi
def defuzzify(tfn):
    return (tfn[0]+tfn[1]+tfn[2])/3


# HALAMAN SEGMENTASI
def page_segmentasi():
    st.title("⚙️ Proses Penentuan Prioritas Penanganan Kemiskinan")

    # Upload Data
    uploaded_file=st.file_uploader(
        "Upload file Excel yang akan digunakan",
        type=["xlsx"]
    )

    if uploaded_file is None:
        st.warning("Silakan upload file Excel terlebih dahulu.")
        return

    data=pd.read_excel(uploaded_file)

    st.subheader("📋 Data yang Diupload")
    st.dataframe(data)

    # Identifikasi Kolom
    id_cols=[
        'KepalaKeluarga',
        'Kecamatan',
        'DesaKelurahan'

    ]

    criteria_cols=data.columns[len(id_cols):].tolist()
    X=data[criteria_cols].copy()
    default_weights=[
        0.16667,
        0.07693,
        0.03189,
        0.21891,
        0.14433,
        0.09154,
        0.06236,
        0.02605,
        0.04135,
        0.06563,
        0.03313,
        0.02048,
        0.01297,
        0.00775
    ]


    st.subheader("⚖️ Bobot Kriteria")
    weights_input={}
    for c,w in zip(criteria_cols,default_weights):
        weights_input[c]=st.number_input(
            c,
            min_value=0.0,
            max_value=1.0,
            value=float(w),
            step=0.00001,
            format="%.5f"
        )
    
    total_weight=sum(weights_input.values())

    st.write("Total Bobot =",round(total_weight,1))
    if abs(total_weight-1)>0.0001:
        st.error("Total bobot harus = 1")
        st.stop()

    weights=weights_input

    # Parameter WASPAS
    st.subheader("⚙️ Parameter WASPAS")
    lambda_val=st.slider(
        "Nilai Lambda",
        0.0,
        1.0,
        0.5,
        0.05
    )

    # Metode Segmentasi 
    st.subheader("📊 Metode Segmentasi") 
    st.write(""" Segmentasi menggunakan metode **desil tetap**: 
             
             - Desil 1 → 10% skor WASPAS tertinggi 
             - Desil 2 → 20% berikutnya 
             - Desil 3 → 30% berikutnya 
             - Desil 4 → 40% berikutnya """)

    # Tombol Proses
    if st.button("🚀 Jalankan Segmentasi"):
        # Fuzzy Matrix
        fuzzy_matrix={
            i:{
                c:to_tfn(X.loc[i,c])
                for c in criteria_cols
            }
            for i in X.index
        }


        # Normalisasi
        norm_matrix=normalize_fuzzy(
            fuzzy_matrix,
            criteria_cols
        )

        # WASPAS
        wsm_scores=fuzzy_wsm(
            norm_matrix,
            weights

        )

        wpm_scores=fuzzy_wpm(
            norm_matrix,
            weights

        )

        final_fuzzy_scores=fuzzy_waspas(
            wsm_scores,
            wpm_scores,
            lambda_val

        )

        # Defuzzifikasi
        result_df=pd.DataFrame({
            'Index':list(final_fuzzy_scores.keys()),
            'WSM_Fuzzy':[
                wsm_scores[i]
                for i in final_fuzzy_scores.keys()
            ],

            'WPM_Fuzzy':[
                wpm_scores[i]
                for i in final_fuzzy_scores.keys()
            ],

            'WASPAS_Fuzzy':[
                final_fuzzy_scores[i]
                for i in final_fuzzy_scores.keys()
            ]
        })

        result_df['WSM']=result_df['WSM_Fuzzy'].apply(defuzzify)
        result_df['WPM']=result_df['WPM_Fuzzy'].apply(defuzzify)
        result_df['WASPAS']=result_df['WASPAS_Fuzzy'].apply(defuzzify)

        final_df=(
            data
            .reset_index()
            .merge(
                result_df,
                left_on='index',
                right_on='Index'
            )
            .drop(columns=['index','Index'])
        )

        # Ranking
        final_df['Rank']=final_df['WASPAS'].rank(
            ascending=False,
            method='dense'
        ).astype(int)


        # Segmentasi Desil Tetap
        score=final_df['WASPAS']
        q1=score.quantile(0.90)
        q2=score.quantile(0.70)
        q3=score.quantile(0.40)

        def assign_cluster(x):
            if x>=q1:
                return 1
            elif x>=q2:
                return 2
            elif x>=q3:
                return 3
            else:
                return 4

        final_df['Cluster']=score.apply(assign_cluster)

        st.subheader("🔍 Hasil Segmentasi")
        st.dataframe(final_df)
        st.session_state['data_proses']=final_df
        st.success("Segmentasi berhasil dilakukan")