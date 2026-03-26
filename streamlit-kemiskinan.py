import streamlit as st
from streamlit_option_menu import option_menu
import warnings

from modules.database import page_database
from modules.dashboard import page_dashboard
from modules.segmentasi import page_segmentasi
from modules.inputasi import page_inputasi

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Segmentasi Kemiskinan", layout="wide")

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Database", "Proses Segmentasi", "Dashboard", "Inputasi"],
        icons=["folder", "gear", "bar-chart", "pencil"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f0f2f6"},
            "icon": {"color": "black", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "2px"},
            "nav-link-selected": {"background-color": "#4b8bbe"},
        }
    )
    st.session_state.page = selected

if 'page' not in st.session_state:
    st.session_state.page = "Database"

# Routing halaman
if st.session_state.page == "Database":
    page_database()
elif st.session_state.page == "Proses Segmentasi":
    page_segmentasi()
elif st.session_state.page == "Dashboard":
    page_dashboard()
elif st.session_state.page == "Inputasi":
    page_inputasi()
