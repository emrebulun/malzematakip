"""
Construction Material Management System - ADVANCED DASHBOARD
Using Supabase REST API with Enhanced Analytics
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from db_manager_rest import get_db_manager_rest
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
def init_db():
    return get_db_manager_rest()

# Cache data functions for performance
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_concrete_summary():
    return db.get_concrete_summary()

@st.cache_data(ttl=300)
def get_cached_rebar_summary():
    return db.get_rebar_summary()

@st.cache_data(ttl=300)
def get_cached_mesh_summary():
    return db.get_mesh_summary()

@st.cache_data(ttl=300)
def get_cached_concrete_logs():
    return db.get_concrete_logs()

@st.cache_data(ttl=300)
def get_cached_rebar_logs():
    return db.get_rebar_logs()

@st.cache_data(ttl=300)
def get_cached_mesh_logs():
    return db.get_mesh_logs()

@st.cache_data(ttl=300)
def get_cached_concrete_by_supplier():
    return db.get_concrete_by_supplier()

@st.cache_data(ttl=300)
def get_cached_concrete_by_location():
    return db.get_concrete_by_location()

db = init_db()

# Sidebar
st.sidebar.title("🏗️ Şantiye 997")

# Add refresh button to sidebar
if st.sidebar.button("🔄 Verileri Yenile", help="Önbelleği temizle ve verileri yenile"):
    st.cache_data.clear()
    st.sidebar.success("Önbellek temizlendi!")
    st.rerun()

st.sidebar.markdown("---")

# Check connection
if db.test_connection():
    st.sidebar.success("✅ Supabase Connected")
else:
    st.sidebar.error("❌ Connection Error")

page = st.sidebar.radio(
    "Navigasyon",
    ["📊 Executive Dashboard", "📈 Detaylı Analizler", "🧱 Beton Girişi", "⚙️ Demir Girişi", "🔲 Hasır Girişi", "📋 Veri Tabloları"]
)

st.sidebar.markdown("---")
st.sidebar.info("💾 Powered by Supabase")

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
# EXECUTIVE DASHBOARD
# ============================================

if page == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard - Şantiye 997")
    st.markdown("### 🏗️ Gerçek Zamanlı Malzeme Takip ve Analiz Sistemi")
    
    # Show loading indicator
    with st.spinner('📊 Veriler yükleniyor...'):
        # Get summaries (cached)
        concrete_summary = get_cached_concrete_summary()
        rebar_summary = get_cached_rebar_summary()
        mesh_summary = get_cached_mesh_summary()
        
        # Get detailed data (cached)
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
        with st.spinner('📊 Beton verileri analiz ediliyor...'):
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
        with st.spinner('📊 Demir verileri analiz ediliyor...'):
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
    
    with tab_hasir:
        with st.spinner('📊 Hasır verileri analiz ediliyor...'):
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

