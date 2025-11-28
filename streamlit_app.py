"""
Construction Material Management System - ADVANCED DASHBOARD
Using Supabase REST API with Enhanced Analytics
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime, date
from db_manager_rest import get_db_manager_rest_v3
from excel_uploader import ExcelValidator
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Şantiye 997 - Yönetim Paneli",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background: linear-gradient(135deg, rgba(255,107,0,0.1) 0%, rgba(255,149,0,0.1) 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255,107,0,0.3);
    }
    h1, h2, h3 {
        color: #FF6B00;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database manager

@st.cache_resource
def init_db_v4():
    return get_db_manager_rest_v3()

# Cache data functions for performance
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_cached_concrete_summary():
    return db.get_concrete_summary()

@st.cache_data(ttl=600)
def get_cached_rebar_summary():
    return db.get_rebar_summary()

@st.cache_data(ttl=600)
def get_cached_mesh_summary():
    return db.get_mesh_summary()

@st.cache_data(ttl=600)
def get_cached_concrete_logs():
    return db.get_concrete_logs()

@st.cache_data(ttl=600)
def get_cached_rebar_logs():
    return db.get_rebar_logs()

@st.cache_data(ttl=600)
def get_cached_mesh_logs():
    return db.get_mesh_logs()

@st.cache_data(ttl=600)
def get_cached_concrete_by_supplier():
    return db.get_concrete_by_supplier()

@st.cache_data(ttl=600)
def get_cached_concrete_by_location():
    return db.get_concrete_by_location()

db = init_db_v4()

# Sidebar
st.sidebar.title("🏗️ Şantiye 997")

# Add refresh button to sidebar
if st.sidebar.button("🔄 Verileri Yenile", help="Önbelleği temizle ve verileri yenile"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.sidebar.success("Tüm önbellek temizlendi!")
    st.rerun()

st.sidebar.markdown("---")

# Check connection
if db.test_connection():
    st.sidebar.success("✅ Veritabanı Bağlı")
else:
    st.sidebar.error("❌ Bağlantı Hatası")

page = st.sidebar.radio(
    "Navigasyon",
    ["📊 Ana Sayfa", "📈 Detaylı Analizler", "🧱 Beton Girişi", "⚙️ Demir Girişi", "🔲 Hasır Girişi", "📂 Toplu Excel Yükleme", "📋 Veri Tabloları"]
)

st.sidebar.markdown("---")
st.sidebar.info("💾 Veriler Supabase'de saklanıyor")

# ============================================
# AUTHENTICATION
# ============================================
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == "emre" and st.session_state["password"] == "024410emre":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Kullanıcı Adı", key="username")
        st.text_input("Şifre", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Kullanıcı Adı", key="username")
        st.text_input("Şifre", type="password", on_change=password_entered, key="password")
        st.error("😕 Kullanıcı adı veya şifre hatalı")
        return False
    else:
        # Password correct.
        return True

# ============================================
# ANA SAYFA
# ============================================

if page == "📊 Ana Sayfa":
    st.title("📊 Şantiye 997 - Yönetim Paneli")
    st.markdown("### 🏗️ Gerçek Zamanlı Malzeme Takip Sistemi")
    
    # Get summaries (cached - fast after first load)
    concrete_summary = get_cached_concrete_summary()
    rebar_summary = get_cached_rebar_summary()
    mesh_summary = get_cached_mesh_summary()
    
    # Get detailed data (cached - fast after first load)
    concrete_df = get_cached_concrete_logs()
    rebar_df = get_cached_rebar_logs()
    mesh_df = get_cached_mesh_logs()
    
    # ============================================
    # MAIN KPIs
    # ============================================
    st.markdown("## 📈 Ana Göstergeler")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🧱 Toplam Beton",
            f"{concrete_summary.get('total_quantity_m3', 0):,.1f} m³",
            delta=f"↑ {concrete_summary.get('total_deliveries', 0)} teslimat"
        )
    
    with col2:
        st.metric(
            "⚙️ Toplam Demir",
            f"{rebar_summary.get('total_weight_kg', 0)/1000:,.1f} ton",
            delta=f"↑ {rebar_summary.get('total_deliveries', 0)} sevkiyat"
        )
    
    with col3:
        st.metric(
            "🔲 Toplam Hasır",
            f"{mesh_summary.get('total_weight_kg', 0)/1000:,.1f} ton",
            delta=f"↑ {mesh_summary.get('total_deliveries', 0)} sevkiyat"
        )
    
    st.markdown("---")
    
    # ============================================
    # TIME SERIES ANALYSIS (ALL MATERIALS)
    # ============================================
    st.markdown("## 📅 Aylık Tüketim Trendleri")
    
    tab1, tab2, tab3 = st.tabs(["🧱 Beton", "⚙️ Demir", "🔲 Hasır"])
    
    with tab1:
        if not concrete_df.empty:
            # Monthly analysis
            concrete_df['date'] = pd.to_datetime(concrete_df['date'])
            concrete_df['year_month'] = concrete_df['date'].dt.to_period('M').astype(str)
            monthly_concrete = concrete_df.groupby('year_month').agg({
                'quantity_m3': 'sum',
                'id': 'count'
            }).reset_index()
            monthly_concrete.columns = ['Ay', 'Toplam m³', 'Teslimat Sayısı']
            
            fig = px.bar(
                monthly_concrete,
                x='Ay',
                y='Toplam m³',
                text='Toplam m³',
                title='Aylık Beton Tüketimi',
                color='Toplam m³',
                color_continuous_scale='Oranges'
            )
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if not rebar_df.empty:
            rebar_df['date'] = pd.to_datetime(rebar_df['date'])
            rebar_df['year_month'] = rebar_df['date'].dt.to_period('M').astype(str)
            monthly_rebar = rebar_df.groupby('year_month')['total_weight_kg'].sum().reset_index()
            
            fig = px.area(
                monthly_rebar,
                x='year_month',
                y='total_weight_kg',
                title='Aylık Demir Alımı (kg)',
                labels={'year_month': 'Ay', 'total_weight_kg': 'Ağırlık (kg)'}
            )
            fig.update_traces(line_color='#E63946')  # fill_color is not a valid property for update_traces here
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz demir verisi yok")
            
    with tab3:
        if not mesh_df.empty:
            mesh_df['date'] = pd.to_datetime(mesh_df['date'])
            mesh_df['year_month'] = mesh_df['date'].dt.to_period('M').astype(str)
            monthly_mesh = mesh_df.groupby('year_month')['weight_kg'].sum().reset_index()
            
            fig = px.line(
                monthly_mesh,
                x='year_month',
                y='weight_kg',
                title='Aylık Hasır Alımı (kg)',
                markers=True
            )
            fig.update_traces(line_color='#00D4FF', line_width=3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz hasır verisi yok")
    
    st.markdown("---")
    
    # ============================================
    # MATERIAL BREAKDOWN
    # ============================================
    st.markdown("## 📊 Malzeme Dağılımları")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🧱 Beton Sınıfları")
        if not concrete_df.empty:
            class_dist = concrete_df.groupby('concrete_class')['quantity_m3'].sum().reset_index()
            fig = px.pie(
                class_dist,
                values='quantity_m3',
                names='concrete_class',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⚙️ Demir Çapları")
        if not rebar_df.empty:
            # Calculate diameter totals
            diameter_cols = [c for c in rebar_df.columns if c.startswith('q') and c.endswith('_kg')]
            if diameter_cols:
                dia_totals = rebar_df[diameter_cols].sum().reset_index()
                dia_totals.columns = ['Çap', 'Ağırlık']
                dia_totals['Çap'] = dia_totals['Çap'].apply(lambda x: f"Ø{x.split('_')[0][1:]}")
                
                fig = px.bar(
                    dia_totals,
                    x='Çap',
                    y='Ağırlık',
                    color='Ağırlık',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Veri yok")
            
    with col3:
        st.markdown("### 🔲 Hasır Tipleri")
        if not mesh_df.empty and 'mesh_type' in mesh_df.columns:
            type_dist = mesh_df.groupby('mesh_type')['weight_kg'].sum().reset_index()
            fig = px.pie(
                type_dist,
                values='weight_kg',
                names='mesh_type',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Veri yok")

    st.markdown("---")
    
    # ============================================
    # LOCATION & SUPPLIER ANALYSIS
    # ============================================
    
    # ============================================
    # LOCATION & SUPPLIER ANALYSIS
    # ============================================
    st.markdown("## 📍 Blok ve Tedarikçi Özeti")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏗️ En Çok Beton Dökülen Bloklar (İlk 15)")
        concrete_by_location = get_cached_concrete_by_location()
        if not concrete_by_location.empty:
            top_locations = concrete_by_location.head(15)
            
            fig = px.bar(
                top_locations,
                x='location_block',
                y='total_quantity_m3',
                title="Blok Bazlı Beton Tüketimi",
                text='total_quantity_m3',
                color='total_quantity_m3',
                color_continuous_scale='Viridis',
                labels={'location_block': 'Blok', 'total_quantity_m3': 'Toplam m³'}
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Malzeme Özet Tablosu")
        
        # Create a combined summary table
        summary_data = []
        
        # Beton
        summary_data.append({
            'Malzeme': 'Beton',
            'Miktar': f"{concrete_summary.get('total_quantity_m3', 0):,.1f} m³",
            'Teslimat': concrete_summary.get('total_deliveries', 0),
            'Tedarikçi': concrete_summary.get('supplier_count', 0)
        })
        
        # Demir
        summary_data.append({
            'Malzeme': 'Demir',
            'Miktar': f"{rebar_summary.get('total_weight_kg', 0):,.0f} kg",
            'Teslimat': rebar_summary.get('total_deliveries', 0),
            'Tedarikçi': '-'
        })
        
        # Hasır
        summary_data.append({
            'Malzeme': 'Hasır',
            'Miktar': f"{mesh_summary.get('total_weight_kg', 0):,.0f} kg",
            'Teslimat': mesh_summary.get('total_deliveries', 0),
            'Tedarikçi': mesh_summary.get('type_count', 0)
        })
        
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("### 🚛 Teslimat Yöntemi (Beton)")
        if not concrete_df.empty:
            delivery_method = concrete_df.groupby('delivery_method')['quantity_m3'].sum().reset_index()
            fig = px.pie(
                delivery_method,
                values='quantity_m3',
                names='delivery_method',
                hole=0.4,
                color_discrete_sequence=['#FF6B00', '#00D4FF']
            )
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# DETAYLI ANALİZLER
# ============================================

elif page == "📈 Detaylı Analizler":
    st.title("📈 Detaylı İstatistiksel Analizler")
    
    tab_beton, tab_demir, tab_hasir = st.tabs(["🧱 Beton", "⚙️ Demir", "🔲 Hasır"])
    
    with tab_beton:
        concrete_df = get_cached_concrete_logs()
        
        if not concrete_df.empty:
            concrete_df['date'] = pd.to_datetime(concrete_df['date'])
            
            # Top performers
            st.markdown("## 🏆 Top Performanslar")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🥇 En Çok Beton Alan Bloklar")
                top_blocks = concrete_df.groupby('location_block')['quantity_m3'].sum().nlargest(10).reset_index()
                fig = px.bar(
                    top_blocks,
                    y='location_block',
                    x='quantity_m3',
                    orientation='h',
                    title="En Çok Beton Alan 10 Blok",
                    color='quantity_m3',
                    color_continuous_scale='Blues',
                    labels={'location_block': 'Blok', 'quantity_m3': 'Miktar (m³)'}
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📅 En Yoğun Günler")
                busiest_days = concrete_df.groupby('date')['quantity_m3'].sum().nlargest(10).reset_index()
                fig = px.bar(
                    busiest_days,
                    x='date',
                    y='quantity_m3',
                    title="En Yoğun 10 Gün",
                    color='quantity_m3',
                    color_continuous_scale='Reds',
                    labels={'date': 'Tarih', 'quantity_m3': 'Miktar (m³)'}
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                st.markdown("### 🧪 Beton Sınıfları")
                top_classes = concrete_df.groupby('concrete_class')['quantity_m3'].sum().nlargest(10).reset_index()
                fig = px.bar(
                    top_classes,
                    y='concrete_class',
                    x='quantity_m3',
                    orientation='h',
                    title="En Çok Kullanılan 10 Sınıf",
                    color='quantity_m3',
                    color_continuous_scale='Greens',
                    labels={'concrete_class': 'Sınıf', 'quantity_m3': 'Miktar (m³)'}
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed statistics
            st.markdown("## 📊 İstatistiksel Özetler")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Miktar Dağılımı")
                fig = px.histogram(
                    concrete_df,
                    x='quantity_m3',
                    nbins=50,
                    title="Beton Miktar Dağılımı",
                    labels={'quantity_m3': 'Miktar (m³)', 'count': 'Frekans'}
                )
                fig.update_traces(marker_color='#FF6B00')
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                st.markdown("**İstatistikler:**")
                st.write(f"- **Ortalama:** {concrete_df['quantity_m3'].mean():.2f} m³")
                st.write(f"- **Medyan:** {concrete_df['quantity_m3'].median():.2f} m³")
                st.write(f"- **Std Sapma:** {concrete_df['quantity_m3'].std():.2f} m³")
                st.write(f"- **Min:** {concrete_df['quantity_m3'].min():.2f} m³")
                st.write(f"- **Max:** {concrete_df['quantity_m3'].max():.2f} m³")
            
            with col2:
                st.markdown("### 📦 Box Plot Analizi")
                fig = px.box(
                    concrete_df,
                    y='quantity_m3',
                    x='concrete_class',
                    title="Beton Sınıfına Göre Miktar Dağılımı",
                    color='concrete_class'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz beton verisi yok")

    with tab_demir:
        rebar_df = get_cached_rebar_logs()
        
        if not rebar_df.empty:
            rebar_df['date'] = pd.to_datetime(rebar_df['date'])
            
            # Timeline
            st.markdown("### 📅 Zaman İçinde Demir Alımı")
            
            # Group by month
            rebar_df['year_month'] = rebar_df['date'].dt.to_period('M').astype(str)
            monthly_rebar = rebar_df.groupby('year_month')['total_weight_kg'].sum().reset_index()
            
            fig = px.bar(
                monthly_rebar,
                x='year_month',
                y='total_weight_kg',
                title="Aylık Demir Alımı (kg)",
                color='total_weight_kg',
                color_continuous_scale='Reds',
                labels={'year_month': 'Ay', 'total_weight_kg': 'Ağırlık (kg)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏢 Tedarikçi Dağılımı")
                if 'supplier' in rebar_df.columns:
                    supplier_rebar = rebar_df.groupby('supplier')['total_weight_kg'].sum().reset_index()
                    fig = px.pie(
                        supplier_rebar,
                        values='total_weight_kg',
                        names='supplier',
                        title="Tedarikçiye Göre Ağırlık",
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Reds_r
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📏 Çap Bazlı Kullanım")
                # Calculate totals for each diameter
                diameter_cols = [c for c in rebar_df.columns if c.startswith('q') and c.endswith('_kg')]
                if diameter_cols:
                    diameter_totals = rebar_df[diameter_cols].sum().reset_index()
                    diameter_totals.columns = ['Çap', 'Ağırlık (kg)']
                    # Format diameter labels (q8_kg -> Ø8)
                    diameter_totals['Çap'] = diameter_totals['Çap'].apply(lambda x: f"Ø{x.split('_')[0][1:]}")
                    
                    fig = px.bar(
                        diameter_totals,
                        x='Çap',
                        y='Ağırlık (kg)',
                        title="Çaplara Göre Toplam Ağırlık",
                        color='Ağırlık (kg)',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz demir verisi yok")
    
    with tab_hasir:
        mesh_df = get_cached_mesh_logs()
        
        if not mesh_df.empty:
            mesh_df['date'] = pd.to_datetime(mesh_df['date'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔷 Hasır Tipi Dağılımı")
                if 'mesh_type' in mesh_df.columns:
                    type_mesh = mesh_df.groupby('mesh_type')['weight_kg'].sum().reset_index()
                    fig = px.pie(
                        type_mesh,
                        values='weight_kg',
                        names='mesh_type',
                        title="Hasır Tipine Göre Ağırlık",
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🏢 Tedarikçi Dağılımı")
                if 'supplier' in mesh_df.columns:
                    supplier_mesh = mesh_df.groupby('supplier')['weight_kg'].sum().reset_index()
                    fig = px.bar(
                        supplier_mesh,
                        x='supplier',
                        y='weight_kg',
                        title="Tedarikçiye Göre Ağırlık",
                        color='weight_kg',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("### 📅 Zaman İçinde Hasır Alımı")
            mesh_df['year_month'] = mesh_df['date'].dt.to_period('M').astype(str)
            monthly_mesh = mesh_df.groupby('year_month')['weight_kg'].sum().reset_index()
            
            fig = px.line(
                monthly_mesh,
                x='year_month',
                y='weight_kg',
                title="Aylık Hasır Alımı (kg)",
                markers=True
            )
            fig.update_traces(line_color='#00D4FF', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz hasır verisi yok")

# ============================================
# DATA ENTRY PAGES (Same as original)
# ============================================

elif page == "🧱 Beton Girişi":
    st.title("🧱 Beton Teslimat Kaydı")
    
    if not check_password():
        st.stop()
    
    with st.form("beton_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tarih = st.date_input("Tarih", date.today())
            firma = st.text_input("Firma")
            irsaliye = st.text_input("İrsaliye No")
            sinif = st.selectbox("Beton Sınıfı", ["C25", "C30", "C35", "C20", "C16", "Diğer"])
        
        with col2:
            miktar = st.number_input("Miktar (m³)", min_value=0.1, step=0.5)
            teslimat = st.selectbox("Teslimat Şekli", ["POMPALI", "MİKSERLİ"])
            blok = st.text_input("Blok")
            aciklama = st.text_area("Açıklama")
        
        submitted = st.form_submit_button("💾 Kaydet")
        
        if submitted:
            data = {
                'date': tarih.isoformat(),
                'supplier': firma,
                'waybill_no': irsaliye,
                'concrete_class': sinif,
                'delivery_method': teslimat,
                'quantity_m3': float(miktar),
                'location_block': blok,
                'notes': aciklama
            }
            
            if db.add_concrete(data):
                # Clear cache after update
                st.cache_data.clear()
                st.success("✅ Kayıt eklendi! Önbellek temizlendi.")
                st.rerun()

elif page == "⚙️ Demir Girişi":
    st.title("⚙️ Demir (İnşaat Demiri) Teslimat Kaydı")
    
    if not check_password():
        st.stop()
    
    with st.form("demir_form"):
        st.markdown("### 📋 Genel Bilgiler")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tarih = st.date_input("📅 Tarih", date.today())
        with col2:
            etap = st.text_input("🏗️ Etap (örn: 3.ETAP)", value="")
        with col3:
            irsaliye = st.text_input("📄 İrsaliye No", value="")
        
        col1, col2 = st.columns(2)
        with col1:
            tedarikci = st.selectbox("🏢 Tedarikçi", [
                "ŞAHİN DEMİR", 
                "KARDEMİR", 
                "İÇDAŞ", 
                "COLAKOGLU", 
                "HABAS",
                "Diğer"
            ])
            if tedarikci == "Diğer":
                tedarikci = st.text_input("Tedarikçi Adı", value="")
        
        with col2:
            uretici = st.text_input("🏭 Üretici Firma", value="")
        
        st.markdown("---")
        st.markdown("### ⚙️ Çap Bazlı Ağırlıklar (kg)")
        st.markdown("*Kullanılmayan çapları boş bırakabilirsiniz*")
        
        # Diameter inputs in 3 columns
        col1, col2, col3, col4 = st.columns(4)
        
        caplar = {}
        diameter_list = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
        
        for idx, cap in enumerate(diameter_list):
            col_idx = idx % 4
            if col_idx == 0:
                with col1:
                    caplar[cap] = st.number_input(f"Ø{cap} mm", min_value=0, value=0, step=100, key=f"q{cap}")
            elif col_idx == 1:
                with col2:
                    caplar[cap] = st.number_input(f"Ø{cap} mm", min_value=0, value=0, step=100, key=f"q{cap}")
            elif col_idx == 2:
                with col3:
                    caplar[cap] = st.number_input(f"Ø{cap} mm", min_value=0, value=0, step=100, key=f"q{cap}")
            else:
                with col4:
                    caplar[cap] = st.number_input(f"Ø{cap} mm", min_value=0, value=0, step=100, key=f"q{cap}")
        
        # Calculate total
        toplam_kg = sum(caplar.values())
        
        st.markdown("---")
        st.markdown(f"### 📊 **Toplam Ağırlık: {toplam_kg:,.0f} kg** ({toplam_kg/1000:.2f} ton)")
        
        submitted = st.form_submit_button("💾 Kaydet", use_container_width=True, type="primary")
        
        if submitted:
            if toplam_kg <= 0:
                st.error("❌ Lütfen en az bir çap için ağırlık girin!")
            else:
                data = {
                    'date': tarih.isoformat(),
                    'etap': etap if etap else None,
                    'irsaliye_no': irsaliye if irsaliye else None,
                    'supplier': tedarikci if tedarikci else None,
                    'uretici': uretici if uretici else None,
                    'total_weight_kg': float(toplam_kg),
                    'q8_kg': float(caplar.get(8, 0)),
                    'q10_kg': float(caplar.get(10, 0)),
                    'q12_kg': float(caplar.get(12, 0)),
                    'q14_kg': float(caplar.get(14, 0)),
                    'q16_kg': float(caplar.get(16, 0)),
                    'q18_kg': float(caplar.get(18, 0)),
                    'q20_kg': float(caplar.get(20, 0)),
                    'q22_kg': float(caplar.get(22, 0)),
                    'q25_kg': float(caplar.get(25, 0)),
                    'q28_kg': float(caplar.get(28, 0)),
                    'q32_kg': float(caplar.get(32, 0))
                }
                
                if db.add_rebar(data):
                    st.cache_data.clear()  # Clear cache
                    st.success(f"✅ {toplam_kg:,.0f} kg demir kaydı başarıyla eklendi!")
                    st.balloons()
                    st.rerun()
    
    # Show recent entries
    st.markdown("---")
    st.markdown("### 📋 Son Kayıtlar")
    recent_rebar = get_cached_rebar_logs()
    if not recent_rebar.empty:
        recent_rebar['date'] = pd.to_datetime(recent_rebar['date'])
        recent_rebar = recent_rebar.sort_values('date', ascending=False).head(10)
        
        # Display summary
        display_cols = ['date', 'supplier', 'irsaliye_no', 'etap', 'total_weight_kg']
        available_cols = [col for col in display_cols if col in recent_rebar.columns]
        
        st.dataframe(
            recent_rebar[available_cols].rename(columns={
                'date': 'Tarih',
                'supplier': 'Tedarikçi',
                'irsaliye_no': 'İrsaliye',
                'etap': 'Etap',
                'total_weight_kg': 'Toplam (kg)'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Henüz demir kaydı yok")

elif page == "🔲 Hasır Girişi":
    st.title("🔲 Hasır (İnşaat Hasırı) Teslimat Kaydı")
    
    if not check_password():
        st.stop()
    
    with st.form("hasir_form"):
        st.markdown("### 📋 Genel Bilgiler")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tarih = st.date_input("📅 Tarih", date.today())
        with col2:
            firma = st.selectbox("🏢 Tedarikçi Firma", [
                "DOFER",
                "MUREL",
                "DKP",
                "ÖZKA",
                "Diğer"
            ])
            if firma == "Diğer":
                firma = st.text_input("Firma Adı", value="")
        with col3:
            irsaliye = st.text_input("📄 İrsaliye No", value="")
        
        st.markdown("---")
        st.markdown("### 🔲 Hasır Detayları")
        
        col1, col2 = st.columns(2)
        
        with col1:
            etap = st.text_input("🏗️ Etap / Bölüm", value="Genel")
            
            hasir_tipi = st.selectbox("🔷 Hasır Tipi", [
                "Q131",
                "Q188",
                "Q221",
                "Q283",
                "Q335",
                "Q503",
                "R188",
                "R335",
                "R503",
                "Diğer"
            ])
            if hasir_tipi == "Diğer":
                hasir_tipi = st.text_input("Hasır Tipi", value="")
        
        with col2:
            ebat = st.text_input("📐 Ebatlar (örn: 215x500 cm)", value="")
            adet = st.number_input("📦 Adet", min_value=1, value=1, step=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            agirlik = st.number_input("⚖️ Toplam Ağırlık (kg)", min_value=0.0, value=0.0, step=10.0)
        
        with col2:
            kullanim_yeri = st.text_input("📍 Kullanım Yeri", value="")
        
        st.markdown("---")
        
        # Auto calculate if possible
        if agirlik > 0 and adet > 0:
            birim_agirlik = agirlik / adet
            st.info(f"ℹ️ Birim Ağırlık: {birim_agirlik:.2f} kg/adet")
        
        submitted = st.form_submit_button("💾 Kaydet", use_container_width=True, type="primary")
        
        if submitted:
            if agirlik <= 0:
                st.error("❌ Lütfen ağırlık bilgisi girin!")
            else:
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'irsaliye_no': irsaliye if irsaliye else None,
                    'etap': etap,
                    'mesh_type': hasir_tipi,
                    'ebatlar': ebat if ebat else None,
                    'piece_count': int(adet),
                    'weight_kg': float(agirlik),
                    'kullanim_yeri': kullanim_yeri if kullanim_yeri else None
                }
                
                if db.add_mesh(data):
                    st.cache_data.clear()  # Clear cache
                    st.success(f"✅ {adet} adet hasır kaydı ({agirlik:.1f} kg) başarıyla eklendi!")
                    st.balloons()
                    st.rerun()
    
    # Show recent entries
    st.markdown("---")
    st.markdown("### 📋 Son Kayıtlar")
    recent_mesh = get_cached_mesh_logs()
    if not recent_mesh.empty:
        recent_mesh['date'] = pd.to_datetime(recent_mesh['date'])
        recent_mesh = recent_mesh.sort_values('date', ascending=False).head(10)
        
        # Display summary
        display_cols = ['date', 'supplier', 'irsaliye_no', 'mesh_type', 'piece_count', 'weight_kg', 'kullanim_yeri']
        available_cols = [col for col in display_cols if col in recent_mesh.columns]
        
        st.dataframe(
            recent_mesh[available_cols].rename(columns={
                'date': 'Tarih',
                'supplier': 'Firma',
                'irsaliye_no': 'İrsaliye',
                'mesh_type': 'Tip',
                'piece_count': 'Adet',
                'weight_kg': 'Ağırlık (kg)',
                'kullanim_yeri': 'Kullanım Yeri'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Henüz hasır kaydı yok")

elif page == "📂 Toplu Excel Yükleme":
    st.title("📂 Toplu Veri Yükleme (Excel)")
    
    if not check_password():
        st.stop()

    st.markdown("""
    Bu modül ile haftalık verilerinizi Excel dosyasından topluca yükleyebilirsiniz.
    
    **Kurallar:**
    1. Dosya `.xlsx` formatında olmalıdır.
    2. Dosyadaki **tüm satırlar** kurallara uygun olmalıdır.
    3. **Tek bir satır bile hatalıysa, hiçbir kayıt yapılmaz.**
    4. Aynı İrsaliye No + Tedarikçi kombinasyonu varsa, eski kayıt güncellenmez, hata verebilir (Sistem ayarlarına bağlı).
    """)

    import_type = st.radio("Yüklenecek Veri Tipi", ["🧱 Beton", "⚙️ Demir", "🔲 Hasır"], horizontal=True)
    
    # Veri Temizleme Bölümü
    with st.expander("🗑️ Veri Temizleme / Silme (Gelişmiş)", expanded=False):
        st.warning("⚠️ Bu bölümdeki işlemler geri alınamaz! Lütfen dikkatli olun.")
        
        del_type = st.radio("Silinecek Veri Tipi", ["🧱 Beton", "⚙️ Demir", "🔲 Hasır"], horizontal=True, key="del_type")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            del_mode = st.radio("Silme Modu", ["Tarih Aralığına Göre", "Tedarikçiye Göre", "TÜMÜNÜ SİL"], key="del_mode")
        
        start_date = None
        end_date = None
        supplier_filter = None
        
        with col_d2:
            if del_mode == "Tarih Aralığına Göre":
                start_date = st.date_input("Başlangıç Tarihi", value=date.today(), key="del_start")
                end_date = st.date_input("Bitiş Tarihi", value=date.today(), key="del_end")
            elif del_mode == "Tedarikçiye Göre":
                suppliers = db.get_all_suppliers()
                supplier_filter = st.selectbox("Tedarikçi Seçin", suppliers, key="del_supp")
            else:
                st.error("DİKKAT: Seçilen veri tipindeki TÜM kayıtlar silinecektir!")

        if st.button("🗑️ Seçilenleri Sil", type="primary", use_container_width=True):
            # Confirmation check
            if del_mode == "TÜMÜNÜ SİL":
                confirm = st.checkbox("Evet, tüm verileri silmek istediğimden eminim.")
                if not confirm:
                    st.warning("Lütfen silme işlemini onaylayın.")
                    st.stop()
            
            result = {}
            s_date_str = start_date.isoformat() if start_date else None
            e_date_str = end_date.isoformat() if end_date else None
            
            if del_type == "🧱 Beton":
                result = db.delete_concrete_logs(start_date=s_date_str, end_date=e_date_str, supplier=supplier_filter)
            elif del_type == "⚙️ Demir":
                result = db.delete_rebar_logs(start_date=s_date_str, end_date=e_date_str, supplier=supplier_filter)
            else:
                result = db.delete_mesh_logs(start_date=s_date_str, end_date=e_date_str, supplier=supplier_filter)
            
            if result.get('success'):
                count = result.get('count', 0)
                st.success(f"✅ İşlem Başarılı! Toplam {count} kayıt silindi.")
                st.cache_data.clear()
                # st.rerun() # Rerun immediately
            else:
                st.error(f"❌ Hata: {result.get('error')}")

    validator = ExcelValidator()
    
    # Şablon Hazırlama
    if import_type == "🧱 Beton":
        template_cols = validator.concrete_columns.keys()
        demo_data = [{'Tarih': '25.11.2025', 'Firma': 'ÖZYURT', 'İrsaliye No': '12345', 'Beton Sınıfı': 'C30', 'Miktar': '12.5', 'Teslimat Şekli': 'POMPALI', 'Blok': 'A1', 'Açıklama': 'Zemin'}]
    elif import_type == "⚙️ Demir":
        template_cols = validator.rebar_columns.keys()
        demo_data = [{'Tarih': '25.11.2025', 'Tedarikçi': 'KARDEMİR', 'İrsaliye No': 'D-001', 'Etap': '3.ETAP', 'Üretici': 'İÇDAŞ', 'Q8': '100', 'Q10': '200', 'Notlar': ''}]
    else:
        template_cols = validator.mesh_columns.keys()
        demo_data = [{'Tarih': '25.11.2025', 'Firma': 'DOFER', 'İrsaliye No': 'H-001', 'Hasır Tipi': 'Q131', 'Ebatlar': '215x500', 'Adet': '50', 'Ağırlık': '1250', 'Kullanım Yeri': 'Perde'}]

    # Şablon İndirme
    df_template = pd.DataFrame(demo_data)
    # CSV yerine Excel indirilebilir ama pandas ile Excel yazmak için openpyxl gerekir. CSV daha güvenli şimdilik veya Excel.
    # Kullanıcı Excel istedi, Excel verelim. openpyxl requirements.txt'de olmayabilir, kontrol edelim. 
    # Listede yoksa CSV verelim.
    
    st.download_button(
        label="📥 Örnek Şablon İndir (Excel)",
        data=df_template.to_csv(index=False).encode('utf-8-sig'), # Excel export kütüphanesi riskine girmeyelim, CSV verip Excel ile açsınlar
        file_name=f"sablon_{import_type.split()[1].lower()}.csv",
        mime="text/csv",
        help="Bu dosyayı Excel ile açıp doldurabilirsiniz. Farklı kaydederken .xlsx seçebilirsiniz."
    )

    uploaded_file = st.file_uploader("Excel Dosyasını Yükleyin", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            # Excel dosyasını yükle (Tüm sayfaları kontrol et)
            xl = pd.ExcelFile(uploaded_file)
            sheet_names = xl.sheet_names
            
            # Hangi sayfayı okuyacağız?
            # Kullanıcıya seçtirme imkanı verelim
            default_ix = 0
            priority_sheets = ['Sayfa1', 'Sayfa 1', 'Veri', 'Data', 'Beton', 'Demir', 'Hasır']
            for i, name in enumerate(sheet_names):
                if any(p.lower() in name.lower() for p in priority_sheets):
                    default_ix = i
                    break
            
            selected_sheet = st.selectbox("Hangi Sayfadan Veri Okunsun?", sheet_names, index=default_ix)
            
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            
            # Remove rows with less than 3 non-empty columns
            original_len = len(df)
            df = df.dropna(thresh=3)
            filtered_len = len(df)
            
            if original_len != filtered_len:
                st.warning(f"⚠️ {original_len - filtered_len} adet eksik veri içeren satır (3 sütundan az veri) yoksayıldı.")

            st.info(f"📄 '{selected_sheet}' sayfası okunuyor ({len(df)} satır)...")

            clean_data = []
            errors = []

            if import_type == "🧱 Beton":
                clean_data, errors = validator.validate_concrete(df)
            elif import_type == "⚙️ Demir":
                clean_data, errors = validator.validate_rebar(df)
            else:
                clean_data, errors = validator.validate_mesh(df)

            if errors:
                st.error(f"❌ Dosyada {len(errors)} adet hata bulundu. Lütfen düzeltip tekrar yükleyin.")
                with st.expander("Hata Listesi (Tıklayıp Genişletin)", expanded=True):
                    for err in errors:
                        st.write(f"- {err}")
            else:
                # Calculate Total Quantity for Verification
                df_preview = pd.DataFrame(clean_data)
                
                total_qty = 0
                unit = ""
                if import_type == "🧱 Beton":
                    total_qty = df_preview['quantity_m3'].sum()
                    unit = "m³"
                elif import_type == "⚙️ Demir":
                    total_qty = df_preview['total_weight_kg'].sum()
                    unit = "kg"
                else:
                    total_qty = df_preview['weight_kg'].sum()
                    unit = "kg"
                
                st.markdown(f"### 📊 Önizleme Özeti")
                col_prev1, col_prev2 = st.columns(2)
                with col_prev1:
                    st.metric("Tespit Edilen Toplam Miktar", f"{total_qty:,.2f} {unit}")
                with col_prev2:
                    st.metric("Okunacak Kayıt Sayısı", f"{len(clean_data)} adet")
                
                st.info("👆 Lütfen yukarıdaki toplam miktarın Excel dosyanızdaki toplamla eşleştiğini kontrol edin.")
                
                st.markdown("#### İlk 5 Kayıt:")
                st.dataframe(df_preview.head(), use_container_width=True)
                
                if st.button(f"🚀 {len(clean_data)} Kaydı Veritabanına Aktar", type="primary"):
                    # Modern status container kullanımı
                    status = st.status("Veriler aktarılıyor...", expanded=True)
                    
                    try:
                        result = {'success': False, 'total_inserted': 0, 'failed': 0}
                        
                        if import_type == "🧱 Beton":
                            status.write("Beton verileri toplu yükleniyor...")
                            result = db.bulk_insert_concrete(clean_data)
                        elif import_type == "⚙️ Demir":
                            status.write("Demir verileri toplu yükleniyor...")
                            result = db.bulk_insert_rebar(clean_data)
                        else:
                            status.write("Hasır verileri toplu yükleniyor...")
                            result = db.bulk_insert_mesh(clean_data)
                            
                        if result.get('success'):
                            success_count = result.get('total_inserted', 0)
                            fail_count = result.get('failed', 0)
                            skipped_count = result.get('skipped', 0)
                            
                            # İşlem bitti
                            status.update(label="İşlem Tamamlandı!", state="complete", expanded=False)
                            
                            # Sonuç mesajları ve önbellek temizliği
                            st.cache_data.clear()
                            
                            if fail_count == 0:
                                msg = f"🎉 İşlem Başarılı! {success_count} yeni kayıt eklendi."
                                if skipped_count > 0:
                                    msg += f" ({skipped_count} adet mükerrer kayıt atlandı)"
                                st.success(msg)
                                
                                if success_count > 0:
                                    st.balloons()
                                    
                                if st.button("Ana Sayfaya Dön ve Yenile"):
                                     st.rerun()
                            else:
                                st.warning(f"⚠️ İşlem Tamamlandı: {success_count} başarılı, {skipped_count} atlandı, {fail_count} başarısız.")
                                st.error("Bazı kayıtlar eklenemedi.")
                                if st.button("Sayfayı Yenile"):
                                     st.rerun()
                        else:
                            status.update(label="Hata Oluştu!", state="error", expanded=False)
                            st.error(f"Toplu yükleme hatası: {result.get('error')}")
                            
                    except Exception as e:
                        status.update(label="Kritik Hata!", state="error", expanded=False)
                        st.error(f"Beklenmeyen hata: {str(e)}")

        except Exception as e:
            st.error(f"Dosya okuma hatası: {str(e)}")

elif page == "📋 Veri Tabloları":
    st.title("📋 Tüm Kayıtlar")
    
    tab1, tab2, tab3 = st.tabs(["🧱 Beton", "⚙️ Demir", "🔲 Hasır"])
    
    with tab1:
        with st.spinner('Veriler yükleniyor...'):
            concrete_df = get_cached_concrete_logs()
        if not concrete_df.empty:
            st.dataframe(concrete_df, use_container_width=True, height=600)
            
            # Download button
            csv = concrete_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV İndir",
                data=csv,
                file_name=f"beton_kayitlari_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Henüz beton kaydı yok")
    
    with tab2:
        rebar_df = get_cached_rebar_logs()
        if not rebar_df.empty:
            st.dataframe(rebar_df, use_container_width=True, height=600)
        else:
            st.info("Henüz demir kaydı yok")
    
    with tab3:
        mesh_df = get_cached_mesh_logs()
        if not mesh_df.empty:
            st.dataframe(mesh_df, use_container_width=True, height=600)
        else:
            st.info("Henüz hasır kaydı yok")

