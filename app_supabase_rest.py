"""
Construction Material Management System
Using Supabase REST API
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from db_manager_rest import get_db_manager_rest
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Şantiye Malzeme Yönetimi",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def init_db():
    return get_db_manager_rest()

db = init_db()

# Sidebar
st.sidebar.title("🏗️ Malzeme Yönetimi")
st.sidebar.markdown("---")

# Check connection
if db.test_connection():
    st.sidebar.success("✅ Supabase Bağlı")
else:
    st.sidebar.error("❌ Bağlantı Hatası")

page = st.sidebar.radio(
    "Sayfa Seçin",
    ["📊 Dashboard", "🧱 Beton Girişi", "⚙️ Demir Girişi", "🔲 Hasır Girişi", "📋 Kayıtlar"]
)

st.sidebar.markdown("---")
st.sidebar.info("💾 Veriler Supabase'de saklanıyor")

# ============================================
# DASHBOARD PAGE
# ============================================

if page == "📊 Dashboard":
    st.title("📊 Genel Bakış Dashboard")
    
    # Get summaries
    concrete_summary = db.get_concrete_summary()
    rebar_summary = db.get_rebar_summary()
    mesh_summary = db.get_mesh_summary()
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🧱 Toplam Beton",
            f"{concrete_summary.get('total_quantity_m3', 0):.1f} m³",
            delta=f"{concrete_summary.get('total_deliveries', 0)} teslimat"
        )
    
    with col2:
        st.metric(
            "⚙️ Toplam Demir",
            f"{rebar_summary.get('total_weight_kg', 0):,.0f} kg",
            delta=f"{rebar_summary.get('total_deliveries', 0)} teslimat"
        )
    
    with col3:
        st.metric(
            "🔲 Toplam Hasır",
            f"{mesh_summary.get('total_weight_kg', 0):,.0f} kg",
            delta=f"{mesh_summary.get('total_deliveries', 0)} teslimat"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Beton - Firma Bazlı")
        concrete_by_supplier = db.get_concrete_by_supplier()
        if not concrete_by_supplier.empty:
            fig = px.bar(
                concrete_by_supplier,
                x='supplier',
                y='total_quantity_m3',
                color='concrete_class',
                title="Firma Bazında Beton Miktarı (m³)",
                labels={'supplier': 'Firma', 'total_quantity_m3': 'Miktar (m³)', 'concrete_class': 'Beton Sınıfı'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz beton verisi yok")
    
    with col2:
        st.subheader("🏘️ Beton - Blok Bazlı")
        concrete_by_location = db.get_concrete_by_location()
        if not concrete_by_location.empty:
            fig = px.pie(
                concrete_by_location,
                names='location_block',
                values='total_quantity_m3',
                title="Bloklara Göre Beton Dağılımı"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz blok verisi yok")

# ============================================
# CONCRETE INPUT PAGE
# ============================================

elif page == "🧱 Beton Girişi":
    st.title("🧱 Beton Teslim Girişi")
    
    with st.form("concrete_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tarih = st.date_input("📅 Tarih", value=date.today())
            firma = st.selectbox("🏢 Firma", ["ÖZYURT BETON", "ALBAYRAK BETON", "Diğer"])
            irsaliye_no = st.text_input("📄 İrsaliye No")
            beton_sinifi = st.selectbox("🎯 Beton Sınıfı", ["C25", "C30", "C35", "C40", "C45", "C50"])
        
        with col2:
            teslim_sekli = st.selectbox("🚛 Teslim Şekli", ["POMPALI", "MİKSERLİ"])
            miktar = st.number_input("📊 Miktar (m³)", min_value=0.0, step=0.5)
            blok = st.text_input("🏘️ Blok/Konum", placeholder="Örn: A Blok, B Blok")
            aciklama = st.text_area("📝 Açıklama", placeholder="Opsiyonel")
        
        submitted = st.form_submit_button("💾 Kaydet", use_container_width=True)
        
        if submitted:
            if not irsaliye_no or miktar <= 0:
                st.error("❌ İrsaliye No ve Miktar zorunludur!")
            else:
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye_no,
                    'concrete_class': beton_sinifi,
                    'delivery_method': teslim_sekli,
                    'quantity_m3': float(miktar),
                    'location_block': blok if blok else None,
                    'notes': aciklama if aciklama else None
                }
                
                if db.add_concrete(data):
                    st.balloons()
                    st.rerun()

# ============================================
# REBAR INPUT PAGE
# ============================================

elif page == "⚙️ Demir Girişi":
    st.title("⚙️ Demir Teslim Girişi")
    
    with st.form("rebar_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tarih = st.date_input("📅 Tarih", value=date.today())
            firma = st.text_input("🏢 Tedarikçi")
            irsaliye_no = st.text_input("📄 İrsaliye No")
            proje_etap = st.text_input("🏗️ Proje Etabı", placeholder="Örn: 3. Etap")
        
        with col2:
            uretici = st.text_input("🏭 Üretici", placeholder="Örn: Kardemir, İskenderun")
            
        st.markdown("### 📏 Çap Bazlı Miktarlar (kg)")
        
        cols = st.columns(4)
        diameters = {}
        diameter_options = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
        
        for idx, diam in enumerate(diameter_options):
            with cols[idx % 4]:
                diameters[f'q{diam}_kg'] = st.number_input(
                    f"Q{diam}", 
                    min_value=0.0, 
                    step=10.0, 
                    key=f"q{diam}"
                )
        
        toplam = sum(diameters.values())
        st.metric("📊 Toplam", f"{toplam:,.1f} kg")
        
        submitted = st.form_submit_button("💾 Kaydet", use_container_width=True)
        
        if submitted:
            if not irsaliye_no or toplam <= 0:
                st.error("❌ İrsaliye No ve en az bir çap miktarı zorunludur!")
            else:
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye_no,
                    'project_stage': proje_etap if proje_etap else None,
                    'manufacturer': uretici if uretici else None,
                    'total_weight_kg': toplam,
                    **diameters
                }
                
                if db.add_rebar(data):
                    st.balloons()
                    st.rerun()

# ============================================
# MESH INPUT PAGE
# ============================================

elif page == "🔲 Hasır Girişi":
    st.title("🔲 Çelik Hasır Teslim Girişi")
    
    with st.form("mesh_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tarih = st.date_input("📅 Tarih", value=date.today())
            firma = st.text_input("🏢 Tedarikçi")
            irsaliye_no = st.text_input("📄 İrsaliye No")
            hasir_tipi = st.selectbox("🔧 Hasır Tipi", ["Q", "R", "TR"])
        
        with col2:
            olculer = st.text_input("📐 Ölçüler", placeholder="Örn: 5x2m")
            adet = st.number_input("📦 Adet", min_value=0, step=1)
            agirlik = st.number_input("⚖️ Ağırlık (kg)", min_value=0.0, step=10.0)
            konum = st.text_input("🏘️ Kullanım Yeri", placeholder="Opsiyonel")
        
        submitted = st.form_submit_button("💾 Kaydet", use_container_width=True)
        
        if submitted:
            if not irsaliye_no or adet <= 0:
                st.error("❌ İrsaliye No ve Adet zorunludur!")
            else:
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye_no,
                    'mesh_type': hasir_tipi,
                    'dimensions': olculer if olculer else None,
                    'piece_count': int(adet),
                    'weight_kg': float(agirlik),
                    'usage_location': konum if konum else None
                }
                
                if db.add_mesh(data):
                    st.balloons()
                    st.rerun()

# ============================================
# RECORDS PAGE
# ============================================

elif page == "📋 Kayıtlar":
    st.title("📋 Tüm Kayıtlar")
    
    tab1, tab2, tab3 = st.tabs(["🧱 Beton", "⚙️ Demir", "🔲 Hasır"])
    
    with tab1:
        st.subheader("Beton Teslimatları")
        concrete_logs = db.get_concrete_logs()
        if not concrete_logs.empty:
            st.dataframe(concrete_logs, use_container_width=True)
        else:
            st.info("Henüz beton kaydı yok")
    
    with tab2:
        st.subheader("Demir Teslimatları")
        rebar_logs = db.get_rebar_logs()
        if not rebar_logs.empty:
            st.dataframe(rebar_logs, use_container_width=True)
        else:
            st.info("Henüz demir kaydı yok")
    
    with tab3:
        st.subheader("Hasır Teslimatları")
        mesh_logs = db.get_mesh_logs()
        if not mesh_logs.empty:
            st.dataframe(mesh_logs, use_container_width=True)
        else:
            st.info("Henüz hasır kaydı yok")

# Footer
st.markdown("---")
st.caption("🏗️ Şantiye Malzeme Yönetim Sistemi | Powered by Supabase REST API")

