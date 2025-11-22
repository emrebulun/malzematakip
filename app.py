import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
import requests
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from api_client import get_api_client

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Construction Material Management | Şantiye 997",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - DARK CORPORATE INDUSTRIAL THEME
# ============================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d29 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #0e1117 100%);
        border-right: 1px solid rgba(255, 107, 0, 0.2);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Glassmorphism Cards for Metrics */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: scale(1.02) translateY(-5px);
        border: 1px solid rgba(255, 107, 0, 0.5);
        box-shadow: 0 12px 48px 0 rgba(255, 107, 0, 0.3);
    }
    
    [data-testid="stMetric"] label {
        color: #a0a0a0 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ff6b00 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Custom Headers */
    h1 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ff6b00 0%, #ff9500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
    
    h2, h3 {
        color: #e0e0e0;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b00 0%, #ff9500 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 0, 0.5);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 107, 0, 0.5);
        color: #ff6b00;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(255, 107, 0, 0.2);
        border-color: #ff6b00;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #ffffff;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(255, 107, 0, 0.5);
    }
    
    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #ff6b00;
        box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.02);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a0a0a0;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b00 0%, #ff9500 100%);
        color: white;
    }
    
    /* Info/Success/Warning Boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #ff6b00;
        background: rgba(255, 107, 0, 0.1);
    }
    
    /* Plotly Charts - Transparent Background */
    .js-plotly-plot {
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 107, 0, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 107, 0, 0.8);
    }
    
    /* Form Container */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
    }
    
    /* Bento Grid Cards */
    .bento-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .bento-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 107, 0, 0.5);
        box-shadow: 0 12px 40px rgba(255, 107, 0, 0.2);
    }
    
    /* Sidebar Logo Area */
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    .sidebar-logo h1 {
        font-size: 1.5rem;
        margin: 0;
    }
    
    /* Animation for page load */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container {
        animation: fadeIn 0.6s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# LOTTIE ANIMATION LOADER
# ============================================
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ============================================
# HELPER FUNCTIONS
# ============================================
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Veri')
    return output.getvalue()

def load_data_from_api():
    """Load data from API backend"""
    api_client = get_api_client()
    
    # Check if API is available
    if not api_client.health_check():
        st.warning("⚠️ Backend API is not available. Using local data mode.")
        load_initial_data_local()
        return
    
    try:
        # Load Beton data
        if st.session_state.beton_df.empty:
            beton_data = api_client.get_all_beton()
            if beton_data and not isinstance(beton_data, dict):
                st.session_state.beton_df = api_client.api_to_dataframe(beton_data, "beton")
        
        # Load Demir data
        if st.session_state.demir_df.empty:
            demir_data = api_client.get_all_demir()
            if demir_data and not isinstance(demir_data, dict):
                st.session_state.demir_df = api_client.api_to_dataframe(demir_data, "demir")
        
        # Load Hasir data
        if st.session_state.hasir_df.empty:
            hasir_data = api_client.get_all_hasir()
            if hasir_data and not isinstance(hasir_data, dict):
                st.session_state.hasir_df = api_client.api_to_dataframe(hasir_data, "hasir")
        
        # Mark that we're using API mode
        st.session_state.api_mode = True
        
    except Exception as e:
        st.error(f"Failed to load data from API: {e}")
        load_initial_data_local()

def load_initial_data_local():
    # Sadece veri boşsa yükleme yap (Mükerrer yüklemeyi önlemek için)
    if st.session_state.beton_df.empty:
        file_path = r"C:\Users\emreb\Desktop\BETON-997.xlsx"
        if os.path.exists(file_path):
            try:
                # Excel dosyasını oku
                df = pd.read_excel(file_path, sheet_name='Sayfa1')
                
                # Kolon eşleştirme (Excel kolon isimleri -> Uygulama kolon isimleri)
                column_mapping = {
                    'TARH': 'TARİH', 'TARİH': 'TARİH',
                    'FRMA': 'FİRMA', 'FİRMA': 'FİRMA',
                    'RSALYE NO': 'İRSALİYE NO', 'İRSALİYE NO': 'İRSALİYE NO',
                    'BETON SINIFI': 'BETON SINIFI',
                    'TESLM EKL': 'TESLİM ŞEKLİ', 'TESLİM ŞEKLİ': 'TESLİM ŞEKLİ',
                    'MKTAR': 'MİKTAR (m3)', 'MİKTAR': 'MİKTAR (m3)',
                    'BLOK': 'BLOK',
                    'AIKLAMA': 'AÇIKLAMA', 'AÇIKLAMA': 'AÇIKLAMA'
                }
                
                # Kolonları yeniden adlandır
                df = df.rename(columns=column_mapping)
                
                # Sadece gerekli kolonları al
                required_cols = ['TARİH', 'FİRMA', 'İRSALİYE NO', 'BETON SINIFI', 
                               'TESLİM ŞEKLİ', 'MİKTAR (m3)', 'BLOK', 'AÇIKLAMA']
                
                # Eksik kolon varsa oluştur
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = None
                        
                # İstenen formatta filtrele
                df = df[required_cols]
                
                # Miktarı olmayan satırları temizle
                df = df.dropna(subset=['MİKTAR (m3)'])
                
                # Blok verisini temizle ve boşları 'Bilinmiyor' olarak işaretle
                df['BLOK'] = df['BLOK'].astype(str).str.strip()
                df['BLOK'] = df['BLOK'].replace(['nan', 'None', 'NaT', ''], 'Bilinmiyor')

                # --- FİRMA DÜZELTME ---
                irsa_nums = pd.to_numeric(df['İRSALİYE NO'], errors='coerce')
                df.loc[irsa_nums > 14000, 'FİRMA'] = 'ALBAYRAK BETON'
                df.loc[irsa_nums <= 14000, 'FİRMA'] = 'ÖZYURT BETON'

                # Session state'e aktar
                st.session_state.beton_df = df
                
            except Exception as e:
                st.error(f"Beton verisi yüklenirken hata oluştu: {e}")

    # --- DEMİR VERİSİ YÜKLEME ---
    if st.session_state.demir_df.empty:
        file_path_demir = r"C:\Users\emreb\Desktop\Demir_997.xlsx"
        if os.path.exists(file_path_demir):
            try:
                df_demir = pd.read_excel(file_path_demir, sheet_name=0, header=1)
                df_demir.columns = df_demir.columns.astype(str)
                
                new_data = []
                
                def get_col_by_keyword(columns, keywords, exclude_keywords=[]):
                    found_cols = []
                    for col in columns:
                        if any(kw in col for kw in keywords):
                            if not any(ex in col for ex in exclude_keywords):
                                found_cols.append(col)
                    return found_cols

                tar_col = get_col_by_keyword(df_demir.columns, ['TAR', 'TARİH'])[0] if get_col_by_keyword(df_demir.columns, ['TAR', 'TARİH']) else None
                etap_col = get_col_by_keyword(df_demir.columns, ['ETAP'])[0] if get_col_by_keyword(df_demir.columns, ['ETAP']) else None
                irsa_col = get_col_by_keyword(df_demir.columns, ['İRSALİYE', 'RSALYE'])[0] if get_col_by_keyword(df_demir.columns, ['İRSALİYE', 'RSALYE']) else None
                tedarik_col = get_col_by_keyword(df_demir.columns, ['SİPARİŞ', 'SPAR', 'SPAR'])[0] if get_col_by_keyword(df_demir.columns, ['SİPARİŞ', 'SPAR', 'SPAR']) else None
                uretici_col = get_col_by_keyword(df_demir.columns, ['GELDİĞİ', 'GELD', 'GELD'])[0] if get_col_by_keyword(df_demir.columns, ['GELDİĞİ', 'GELD', 'GELD']) else None

                q8_cols = get_col_by_keyword(df_demir.columns, ["8'", "8 "], exclude_keywords=["18", "28"])
                q10_cols = get_col_by_keyword(df_demir.columns, ["10'", "10 "])
                q12_cols = get_col_by_keyword(df_demir.columns, ["12'", "12 "])
                q14_cols = get_col_by_keyword(df_demir.columns, ["14'", "14 "])
                q16_cols = get_col_by_keyword(df_demir.columns, ["16'", "16 "])
                q18_cols = get_col_by_keyword(df_demir.columns, ["18'", "18 ", "18L"], exclude_keywords=[])
                q20_cols = get_col_by_keyword(df_demir.columns, ["20'", "20 "])
                q22_cols = get_col_by_keyword(df_demir.columns, ["22'", "22 "])
                q25_cols = get_col_by_keyword(df_demir.columns, ["25'", "25 ", "24'", "24 "])
                q28_cols = get_col_by_keyword(df_demir.columns, ["28'", "28 "])
                q32_cols = get_col_by_keyword(df_demir.columns, ["32'", "32 "])
                
                cap_cols_map = {
                    8: q8_cols, 10: q10_cols, 12: q12_cols, 14: q14_cols,
                    16: q16_cols, 18: q18_cols, 20: q20_cols, 22: q22_cols,
                    25: q25_cols, 28: q28_cols, 32: q32_cols
                }

                for _, row in df_demir.iterrows():
                    if tar_col and pd.isna(row.get(tar_col)):
                        continue
                        
                    item = {}
                    item['TARİH'] = row.get(tar_col)
                    item['ETAP'] = row.get(etap_col)
                    item['İRSALİYE NO'] = row.get(irsa_col)
                    item['TEDARİKÇİ'] = row.get(tedarik_col)
                    item['ÜRETİCİ'] = row.get(uretici_col)
                    
                    for cap, cols in cap_cols_map.items():
                        val = 0
                        for c in cols:
                            v = pd.to_numeric(row.get(c), errors='coerce')
                            if pd.notna(v):
                                val += v
                        item[f'Q{cap}'] = val
                        
                    q_keys = [k for k in item.keys() if k.startswith('Q')]
                    item['TOPLAM AĞIRLIK (kg)'] = sum([item[k] for k in q_keys])
                    
                    if item['TOPLAM AĞIRLIK (kg)'] > 0:
                         new_data.append(item)
                
                if new_data:
                    st.session_state.demir_df = pd.DataFrame(new_data)
                    
            except Exception as e:
                st.error(f"Demir verisi yüklenirken hata oluştu: {e}")

    # --- HASIR VERİSİ YÜKLEME ---
    if st.session_state.hasir_df.empty:
        file_path_hasir = r"C:\Users\emreb\Desktop\Hasır_997.xlsx"
        if os.path.exists(file_path_hasir):
            try:
                df_hasir = pd.read_excel(file_path_hasir)
                df_hasir.columns = df_hasir.columns.astype(str)
                
                new_hasir = []
                
                def get_col_by_keyword(columns, keywords):
                    for col in columns:
                        for kw in keywords:
                            if kw in col:
                                return col
                    return None

                tar_col = get_col_by_keyword(df_hasir.columns, ['TARİH', 'TARH', 'TARH'])
                firma_col = get_col_by_keyword(df_hasir.columns, ['FİRMA', 'FRMA', 'FRMA'])
                irsa_col = get_col_by_keyword(df_hasir.columns, ['İRSALİYE', 'RSALYE', 'RSALYE'])
                etap_col = get_col_by_keyword(df_hasir.columns, ['ETAP'])
                tip_col = get_col_by_keyword(df_hasir.columns, ['HASIR TİPİ', 'HASIR TP', 'HASIR TP'])
                boy_col = get_col_by_keyword(df_hasir.columns, ['HASIR UZUNLUĞU', 'HASIR UZUNLUU', 'HASIR UZUNLUU'])
                en_col = get_col_by_keyword(df_hasir.columns, ['HASIRIN ENİ', 'HASIRIN EN', 'HASIRIN EN'])
                adet_col = get_col_by_keyword(df_hasir.columns, ['ADET'])
                weight_cols = [c for c in df_hasir.columns if 'AĞIRLIK' in c or 'AIRLIK' in c or 'ARLIK' in c or 'AIRLIK' in c]
                ss_col = get_col_by_keyword(df_hasir.columns, ['SS', 'KULLANIM YERİ'])
                
                for _, row in df_hasir.iterrows():
                    if tar_col and pd.isna(row.get(tar_col)):
                        continue
                        
                    item = {}
                    item['TARİH'] = row.get(tar_col) if tar_col else None
                    item['FİRMA'] = row.get(firma_col) if firma_col else None
                    item['İRSALİYE NO'] = row.get(irsa_col) if irsa_col else None
                    item['ETAP'] = row.get(etap_col) if etap_col else "Genel"
                    item['HASIR TİPİ'] = row.get(tip_col) if tip_col else None
                    
                    boy_val = row.get(boy_col) if boy_col else None
                    en_val = row.get(en_col) if en_col else None
                    if pd.notna(boy_val) and pd.notna(en_val):
                        item['EBATLAR'] = f"{en_val}x{boy_val}"
                    else:
                        item['EBATLAR'] = ""
                        
                    item['ADET'] = pd.to_numeric(row.get(adet_col), errors='coerce') if adet_col else 0
                    
                    val = 0
                    if weight_cols:
                        vals = []
                        for c in weight_cols:
                            v = pd.to_numeric(row[c], errors='coerce')
                            if pd.notna(v):
                                vals.append(v)
                        if vals:
                            val = max(vals)
                    
                    item['AĞIRLIK (kg)'] = val
                    item['KULLANIM YERİ'] = row.get(ss_col) if ss_col else None
                    
                    if (item['AĞIRLIK (kg)'] > 0 or (item['ADET'] and item['ADET'] > 0)) and item['TARİH'] is not None:
                        new_hasir.append(item)
                        
                if new_hasir:
                    st.session_state.hasir_df = pd.DataFrame(new_hasir)

            except Exception as e:
                st.error(f"Hasır verisi yüklenirken hata oluştu: {e}")

# ============================================
# CUSTOM PLOTLY THEME
# ============================================
def get_plotly_theme():
    return {
        'layout': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#e0e0e0', 'family': 'Inter'},
            'title': {'font': {'size': 20, 'color': '#ffffff'}},
            'xaxis': {
                'gridcolor': 'rgba(255, 255, 255, 0.1)',
                'zerolinecolor': 'rgba(255, 255, 255, 0.1)',
            },
            'yaxis': {
                'gridcolor': 'rgba(255, 255, 255, 0.1)',
                'zerolinecolor': 'rgba(255, 255, 255, 0.1)',
            },
            'colorway': ['#ff6b00', '#ff9500', '#00d4ff', '#00ff88', '#ff00ff', '#ffff00']
        }
    }

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'beton_df' not in st.session_state:
    st.session_state.beton_df = pd.DataFrame(columns=[
        'TARİH', 'FİRMA', 'İRSALİYE NO', 'BETON SINIFI', 
        'TESLİM ŞEKLİ', 'MİKTAR (m3)', 'BLOK', 'AÇIKLAMA'
    ])

if 'demir_df' not in st.session_state:
    cols = ['TARİH', 'ETAP', 'İRSALİYE NO', 'TEDARİKÇİ', 'ÜRETİCİ']
    caplar = [f"Q{i}" for i in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]]
    cols.extend(caplar)
    cols.append('TOPLAM AĞIRLIK (kg)')
    st.session_state.demir_df = pd.DataFrame(columns=cols)

if 'hasir_df' not in st.session_state:
    st.session_state.hasir_df = pd.DataFrame(columns=[
        'TARİH', 'FİRMA', 'İRSALİYE NO', 'ETAP', 
        'HASIR TİPİ', 'EBATLAR', 'ADET', 'AĞIRLIK (kg)', 'KULLANIM YERİ'
    ])

# Initialize API mode flag
if 'api_mode' not in st.session_state:
    st.session_state.api_mode = False

# Load initial data (try API first, fallback to local)
load_data_from_api()

# Inject CSS
inject_custom_css()

# ============================================
# SIDEBAR WITH LOTTIE ANIMATION
# ============================================
with st.sidebar:
    # Load Lottie Animation
    lottie_construction = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_w51pcehl.json")
    if lottie_construction:
        st_lottie(lottie_construction, height=150, key="construction")
    
    st.markdown("<div class='sidebar-logo'><h1>🏗️ Şantiye 997</h1></div>", unsafe_allow_html=True)
    
    # Modern Menu with Icons
    menu = option_menu(
        menu_title=None,
        options=["Dashboard", "Beton", "Demir", "Hasır"],
        icons=["speedometer2", "droplet-fill", "grid-3x3-gap-fill", "grid-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#ff6b00", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "padding": "12px",
                "border-radius": "10px",
                "color": "#a0a0a0",
                "background-color": "rgba(255, 255, 255, 0.05)",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #ff6b00 0%, #ff9500 100%)",
                "color": "white",
                "font-weight": "600",
            },
        }
    )
    
    st.markdown("---")
    
    # API Status Indicator
    if st.session_state.api_mode:
        st.success("🟢 **API Connected**\nBackend Active")
    else:
        st.warning("🟡 **Local Mode**\nAPI Offline")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Records", len(st.session_state.beton_df) + len(st.session_state.demir_df) + len(st.session_state.hasir_df))
    st.markdown("---")
    st.info("🚀 **Enterprise Edition**\nPowered by Advanced Analytics")

# ============================================
# MAIN CONTENT - DASHBOARD
# ============================================
if menu == "Dashboard":
    st.markdown("<h1>📊 Executive Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("### Real-time Construction Material Analytics")
    
    # KPI Cards - Bento Grid Style
    col1, col2, col3, col4 = st.columns(4)
    
    toplam_beton = st.session_state.beton_df['MİKTAR (m3)'].sum()
    toplam_demir = st.session_state.demir_df['TOPLAM AĞIRLIK (kg)'].sum()
    toplam_hasir = st.session_state.hasir_df['AĞIRLIK (kg)'].sum()
    total_deliveries = len(st.session_state.beton_df)
    
    with col1:
        st.metric("🏗️ Total Concrete", f"{toplam_beton:.1f} m³", delta=f"{total_deliveries} deliveries")
    
    with col2:
        st.metric("⚙️ Total Rebar", f"{toplam_demir/1000:.1f} tons", delta=f"{len(st.session_state.demir_df)} shipments")
    
    with col3:
        st.metric("🕸️ Steel Mesh", f"{toplam_hasir/1000:.1f} tons", delta=f"{len(st.session_state.hasir_df)} orders")
    
    with col4:
        total_value = toplam_beton * 1000 + toplam_demir * 15 + toplam_hasir * 18  # Estimated
        st.metric("💰 Est. Value", f"₺{total_value/1000000:.1f}M", delta="Estimated")
    
    st.markdown("---")
    
    # Charts Grid
    if not st.session_state.beton_df.empty:
        st.markdown("### 🏢 Concrete Distribution Analysis")
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Concrete by Class
            fig_class = px.pie(
                st.session_state.beton_df, 
                names='BETON SINIFI', 
                values='MİKTAR (m3)', 
                title='Concrete by Class',
                hole=0.4
            )
            fig_class.update_layout(**get_plotly_theme()['layout'])
            fig_class.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_class, use_container_width=True)
        
        with c2:
            # Concrete by Company
            firma_grp = st.session_state.beton_df.groupby('FİRMA')['MİKTAR (m3)'].sum().reset_index()
            fig_firma = px.bar(
                firma_grp,
                x='FİRMA',
                y='MİKTAR (m3)',
                title='Concrete by Supplier',
                text_auto='.1f',
                color='FİRMA',
                color_discrete_sequence=['#ff6b00', '#ff9500', '#00d4ff']
            )
            fig_firma.update_layout(**get_plotly_theme()['layout'])
            st.plotly_chart(fig_firma, use_container_width=True)
        
        # Block Analysis
        st.markdown("### 🏗️ Concrete Distribution by Block")
        blok_grp = st.session_state.beton_df.groupby('BLOK')['MİKTAR (m3)'].sum().reset_index()
        blok_grp = blok_grp.sort_values(by='MİKTAR (m3)', ascending=False)
        
        fig_blok = px.bar(
            blok_grp,
            x='BLOK',
            y='MİKTAR (m3)',
            title='Which Block Received How Much Concrete?',
            text_auto='.0f',
            color='MİKTAR (m3)',
            color_continuous_scale='Oranges'
        )
        fig_blok.update_layout(**get_plotly_theme()['layout'], height=400)
        st.plotly_chart(fig_blok, use_container_width=True)
    
    if not st.session_state.demir_df.empty:
        st.markdown("---")
        st.markdown("### ⚙️ Rebar (Iron) Analytics")
        
        df_demir_analiz = st.session_state.demir_df.copy()
        q_cols = [c for c in df_demir_analiz.columns if c.startswith('Q') and c[1:].isdigit()]
        
        c1, c2 = st.columns(2)
        
        with c1:
            if q_cols:
                cap_totals = df_demir_analiz[q_cols].sum().reset_index()
                cap_totals.columns = ['Diameter', 'Weight (kg)']
                
                fig_cap = px.bar(
                    cap_totals,
                    x='Diameter',
                    y='Weight (kg)',
                    title='Rebar Usage by Diameter',
                    text_auto='.2s',
                    color='Weight (kg)',
                    color_continuous_scale='Reds'
                )
                fig_cap.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig_cap, use_container_width=True)
        
        with c2:
            if 'TEDARİKÇİ' in df_demir_analiz.columns:
                tedarik_grp = df_demir_analiz.groupby('TEDARİKÇİ')['TOPLAM AĞIRLIK (kg)'].sum().reset_index()
                fig_tedarik = px.pie(
                    tedarik_grp,
                    values='TOPLAM AĞIRLIK (kg)',
                    names='TEDARİKÇİ',
                    title='Supplier Distribution',
                    hole=0.4
                )
                fig_tedarik.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig_tedarik, use_container_width=True)
    
    if not st.session_state.hasir_df.empty:
        st.markdown("---")
        st.markdown("### 🕸️ Steel Mesh Analytics")
        
        df_hasir_analiz = st.session_state.hasir_df.copy()
        
        c1, c2 = st.columns(2)
        
        with c1:
            if 'HASIR TİPİ' in df_hasir_analiz.columns:
                tip_grp = df_hasir_analiz.groupby('HASIR TİPİ')['AĞIRLIK (kg)'].sum().reset_index()
                fig_tip = px.pie(
                    tip_grp,
                    values='AĞIRLIK (kg)',
                    names='HASIR TİPİ',
                    title='Mesh Type Distribution',
                    hole=0.4
                )
                fig_tip.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig_tip, use_container_width=True)
        
        with c2:
            if 'FİRMA' in df_hasir_analiz.columns:
                firma_grp = df_hasir_analiz.groupby('FİRMA')['AĞIRLIK (kg)'].sum().reset_index()
                fig_firma = px.bar(
                    firma_grp,
                    x='FİRMA',
                    y='AĞIRLIK (kg)',
                    title='Mesh Purchase by Supplier',
                    text_auto='.2s',
                    color='FİRMA',
                    color_discrete_sequence=['#ff6b00', '#00d4ff', '#00ff88']
                )
                fig_firma.update_layout(**get_plotly_theme()['layout'])
                st.plotly_chart(fig_firma, use_container_width=True)

# ============================================
# BETON MODULE
# ============================================
elif menu == "Beton":
    st.markdown("<h1>🚛 Concrete Management</h1>", unsafe_allow_html=True)
    
    # Excel Import Section
    with st.expander("📤 Import from Excel", expanded=False):
        uploaded_file = st.file_uploader("Upload Concrete Excel File", type=['xlsx', 'xls'], key="beton_upload")
        if uploaded_file is not None:
            if st.button("Import Data", key="import_beton"):
                # Save uploaded file temporarily
                temp_path = f"temp_beton_{datetime.now().timestamp()}.xlsx"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                if st.session_state.api_mode:
                    api_client = get_api_client()
                    result = api_client.import_beton_excel(temp_path)
                    if 'error' not in result:
                        st.success(f"✅ Imported {result.get('count', 0)} records!")
                        # Refresh data
                        beton_data = api_client.get_all_beton()
                        st.session_state.beton_df = api_client.api_to_dataframe(beton_data, "beton")
                    else:
                        st.error(f"Import failed: {result.get('error')}")
                else:
                    st.warning("Excel import requires API mode. Please start the backend server.")
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                st.rerun()
    
    with st.expander("➕ Add New Concrete Delivery", expanded=False):
        with st.form("beton_form"):
            c1, c2, c3 = st.columns(3)
            tarih = c1.date_input("Date", datetime.now())
            firma = c2.selectbox("Supplier", ["ÖZYURT BETON", "ALBAYRAK BETON", "OTHER"])
            irsa_no = c3.text_input("Waybill No")
            
            c4, c5, c6 = st.columns(3)
            beton_sinifi = c4.selectbox("Class", ["C25", "C30", "C35", "GRO", "ŞAP"])
            teslim = c5.selectbox("Delivery Method", ["POMPALI", "MİKSERLİ"])
            miktar = c6.number_input("Quantity (m3)", min_value=0.1, step=0.5)
            
            c7, c8 = st.columns(2)
            blok = c7.text_input("Block / Location (e.g., GK1)")
            aciklama = c8.text_input("Description")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                if st.session_state.api_mode:
                    # Use API
                    api_client = get_api_client()
                    data = {
                        'tarih': tarih.isoformat(),
                        'firma': firma,
                        'irsaliye_no': irsa_no,
                        'beton_sinifi': beton_sinifi,
                        'teslim_sekli': teslim,
                        'miktar': float(miktar),
                        'blok': blok,
                        'aciklama': aciklama
                    }
                    result = api_client.create_beton(data)
                    if 'error' not in result:
                        st.success("✅ Concrete record added successfully!")
                        # Refresh data from API
                        beton_data = api_client.get_all_beton()
                        st.session_state.beton_df = api_client.api_to_dataframe(beton_data, "beton")
                        st.rerun()
                    else:
                        st.error(f"Failed to save: {result.get('error')}")
                else:
                    # Use local mode
                    new_row = {
                        'TARİH': tarih, 'FİRMA': firma, 'İRSALİYE NO': irsa_no,
                        'BETON SINIFI': beton_sinifi, 'TESLİM ŞEKLİ': teslim,
                        'MİKTAR (m3)': miktar, 'BLOK': blok, 'AÇIKLAMA': aciklama
                    }
                    st.session_state.beton_df = pd.concat([st.session_state.beton_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("✅ Concrete record added successfully!")
                    st.rerun()
    
    st.markdown("### 📋 Delivery Records")
    st.dataframe(st.session_state.beton_df, use_container_width=True, height=400)
    
    st.download_button(
        label="📥 Download as Excel",
        data=convert_df_to_excel(st.session_state.beton_df),
        file_name='Concrete_Records.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# ============================================
# DEMIR MODULE
# ============================================
elif menu == "Demir":
    st.markdown("<h1>⚙️ Rebar (Iron) Management</h1>", unsafe_allow_html=True)
    
    # Excel Import Section
    with st.expander("📤 Import from Excel", expanded=False):
        uploaded_file = st.file_uploader("Upload Rebar Excel File", type=['xlsx', 'xls'], key="demir_upload")
        if uploaded_file is not None:
            if st.button("Import Data", key="import_demir"):
                temp_path = f"temp_demir_{datetime.now().timestamp()}.xlsx"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                if st.session_state.api_mode:
                    api_client = get_api_client()
                    result = api_client.import_demir_excel(temp_path)
                    if 'error' not in result:
                        st.success(f"✅ Imported {result.get('count', 0)} records!")
                        demir_data = api_client.get_all_demir()
                        st.session_state.demir_df = api_client.api_to_dataframe(demir_data, "demir")
                    else:
                        st.error(f"Import failed: {result.get('error')}")
                else:
                    st.warning("Excel import requires API mode. Please start the backend server.")
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                st.rerun()
    
    with st.expander("➕ Add New Rebar Delivery", expanded=False):
        with st.form("demir_form"):
            c1, c2, c3 = st.columns(3)
            tarih = c1.date_input("Date", datetime.now())
            irsa_no = c2.text_input("Waybill No")
            etap = c3.text_input("Phase (e.g., 3.ETAP)")
            
            c4, c5 = st.columns(2)
            tedarikci = c4.selectbox("Supplier", ["ŞAHİN DEMİR", "KARDEMİR", "İÇDAŞ", "OTHER"])
            uretici = c5.text_input("Manufacturer")
            
            st.markdown("##### Weight by Diameter (kg)")
            cols = st.columns(6)
            caplar = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
            kg_values = {}
            
            for i, cap in enumerate(caplar):
                with cols[i % 6]:
                    kg_values[f"Q{cap}"] = st.number_input(f"Q{cap}", min_value=0, step=100, key=f"d_{cap}")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                toplam_kg = sum(kg_values.values())
                
                if st.session_state.api_mode:
                    # Use API
                    api_client = get_api_client()
                    data = {
                        'tarih': tarih.isoformat(),
                        'etap': etap,
                        'irsaliye_no': irsa_no,
                        'tedarikci': tedarikci,
                        'uretici': uretici,
                        'toplam_agirlik': float(toplam_kg)
                    }
                    # Add Q values
                    for cap in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
                        data[f'q{cap}'] = float(kg_values.get(f'Q{cap}', 0))
                    
                    result = api_client.create_demir(data)
                    if 'error' not in result:
                        st.success(f"✅ Total {toplam_kg} kg rebar recorded!")
                        # Refresh data from API
                        demir_data = api_client.get_all_demir()
                        st.session_state.demir_df = api_client.api_to_dataframe(demir_data, "demir")
                        st.rerun()
                    else:
                        st.error(f"Failed to save: {result.get('error')}")
                else:
                    # Use local mode
                    new_row = {
                        'TARİH': tarih, 'ETAP': etap, 'İRSALİYE NO': irsa_no,
                        'TEDARİKÇİ': tedarikci, 'ÜRETİCİ': uretici,
                        'TOPLAM AĞIRLIK (kg)': toplam_kg
                    }
                    new_row.update(kg_values)
                    
                    st.session_state.demir_df = pd.concat([st.session_state.demir_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"✅ Total {toplam_kg} kg rebar recorded!")
                    st.rerun()

    st.markdown("### 📋 Delivery Records")
    st.dataframe(st.session_state.demir_df, use_container_width=True, height=400)
    
    st.download_button(
        label="📥 Download as Excel",
        data=convert_df_to_excel(st.session_state.demir_df),
        file_name='Rebar_Records.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Analytics
    if not st.session_state.demir_df.empty:
        st.markdown("---")
        st.markdown("### 📊 Rebar Analytics")
        
        tab1, tab2 = st.tabs(["📏 Diameter Analysis", "📈 Supplier & Timeline"])
        
        with tab1:
            df_demir_analiz = st.session_state.demir_df.copy()
            q_cols = [c for c in df_demir_analiz.columns if c.startswith('Q') and c[1:].isdigit()]
            
            if q_cols:
                cap_totals = df_demir_analiz[q_cols].sum().reset_index()
                cap_totals.columns = ['Diameter', 'Weight (kg)']
                
                fig_cap = px.bar(
                    cap_totals,
                    x='Diameter',
                    y='Weight (kg)',
                    title='Rebar Usage by Diameter',
                    text_auto='.2s',
                    color='Weight (kg)',
                    color_continuous_scale='Reds'
                )
                fig_cap.update_layout(**get_plotly_theme()['layout'], height=500)
                st.plotly_chart(fig_cap, use_container_width=True)
        
        with tab2:
            c1, c2 = st.columns(2)
            
            with c1:
                if 'TEDARİKÇİ' in df_demir_analiz.columns:
                    tedarik_grp = df_demir_analiz.groupby('TEDARİKÇİ')['TOPLAM AĞIRLIK (kg)'].sum().reset_index()
                    fig_tedarik = px.pie(
                        tedarik_grp,
                        values='TOPLAM AĞIRLIK (kg)',
                        names='TEDARİKÇİ',
                        title='Supplier Distribution',
                        hole=0.4
                    )
                    fig_tedarik.update_layout(**get_plotly_theme()['layout'])
                    st.plotly_chart(fig_tedarik, use_container_width=True)
            
            with c2:
                if 'TARİH' in df_demir_analiz.columns:
                    df_demir_analiz['TARİH'] = pd.to_datetime(df_demir_analiz['TARİH'])
                    daily_demir = df_demir_analiz.groupby('TARİH')['TOPLAM AĞIRLIK (kg)'].sum().reset_index()
                    fig_timeline = px.line(
                        daily_demir,
                        x='TARİH',
                        y='TOPLAM AĞIRLIK (kg)',
                        title='Rebar Delivery Timeline',
                        markers=True
                    )
                    fig_timeline.update_layout(**get_plotly_theme()['layout'])
                    fig_timeline.update_traces(line_color='#ff6b00', line_width=3)
                    st.plotly_chart(fig_timeline, use_container_width=True)

# ============================================
# HASIR MODULE
# ============================================
elif menu == "Hasır":
    st.markdown("<h1>🕸️ Steel Mesh Management</h1>", unsafe_allow_html=True)
    
    # Excel Import Section
    with st.expander("📤 Import from Excel", expanded=False):
        uploaded_file = st.file_uploader("Upload Mesh Excel File", type=['xlsx', 'xls'], key="hasir_upload")
        if uploaded_file is not None:
            if st.button("Import Data", key="import_hasir"):
                temp_path = f"temp_hasir_{datetime.now().timestamp()}.xlsx"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                if st.session_state.api_mode:
                    api_client = get_api_client()
                    result = api_client.import_hasir_excel(temp_path)
                    if 'error' not in result:
                        st.success(f"✅ Imported {result.get('count', 0)} records!")
                        hasir_data = api_client.get_all_hasir()
                        st.session_state.hasir_df = api_client.api_to_dataframe(hasir_data, "hasir")
                    else:
                        st.error(f"Import failed: {result.get('error')}")
                else:
                    st.warning("Excel import requires API mode. Please start the backend server.")
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                st.rerun()
    
    with st.expander("➕ Add New Mesh Delivery", expanded=False):
        with st.form("hasir_form"):
            c1, c2 = st.columns(2)
            tarih = c1.date_input("Date", datetime.now())
            firma = c2.selectbox("Supplier", ["DOFER", "MUREL", "OTHER"])
            
            c3, c4, c5 = st.columns(3)
            irsa_no = c3.text_input("Waybill No")
            tip = c4.selectbox("Mesh Type", ["Q Type", "R Type", "TR Type"])
            ebat = c5.text_input("Dimensions (e.g., 215x500)")
            
            c6, c7, c8 = st.columns(3)
            adet = c6.number_input("Quantity (pcs)", min_value=1)
            agirlik = c7.number_input("Total Weight (kg)", min_value=1.0)
            yer = c8.text_input("Usage Location")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                if st.session_state.api_mode:
                    # Use API
                    api_client = get_api_client()
                    data = {
                        'tarih': tarih.isoformat(),
                        'firma': firma,
                        'irsaliye_no': irsa_no,
                        'etap': "General",
                        'hasir_tipi': tip,
                        'ebatlar': ebat,
                        'adet': int(adet),
                        'agirlik': float(agirlik),
                        'kullanim_yeri': yer
                    }
                    result = api_client.create_hasir(data)
                    if 'error' not in result:
                        st.success("✅ Mesh record added successfully!")
                        # Refresh data from API
                        hasir_data = api_client.get_all_hasir()
                        st.session_state.hasir_df = api_client.api_to_dataframe(hasir_data, "hasir")
                        st.rerun()
                    else:
                        st.error(f"Failed to save: {result.get('error')}")
                else:
                    # Use local mode
                    new_row = {
                        'TARİH': tarih, 'FİRMA': firma, 'İRSALİYE NO': irsa_no,
                        'ETAP': "General", 'HASIR TİPİ': tip, 'EBATLAR': ebat,
                        'ADET': adet, 'AĞIRLIK (kg)': agirlik, 'KULLANIM YERİ': yer
                    }
                    st.session_state.hasir_df = pd.concat([st.session_state.hasir_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("✅ Mesh record added successfully!")
                    st.rerun()

    st.markdown("### 📋 Delivery Records")
    st.dataframe(st.session_state.hasir_df, use_container_width=True, height=400)
    
    st.download_button(
        label="📥 Download as Excel",
        data=convert_df_to_excel(st.session_state.hasir_df),
        file_name='Mesh_Records.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
