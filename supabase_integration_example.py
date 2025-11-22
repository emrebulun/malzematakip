"""
Supabase Integration Example for Streamlit App
Shows how to integrate db_manager.py into your main app.py
"""

import streamlit as st
from datetime import datetime
from db_manager import get_db_manager

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Construction Material Tracking - Supabase",
    page_icon="🏗️",
    layout="wide"
)

# ============================================
# INITIALIZE DATABASE CONNECTION
# ============================================

# Get cached database manager instance
db = get_db_manager()

# Test connection on startup
if db.test_connection():
    st.sidebar.success("🟢 Connected to Supabase")
else:
    st.sidebar.error("🔴 Supabase connection failed")
    st.stop()

# ============================================
# SIDEBAR NAVIGATION
# ============================================

st.sidebar.title("🏗️ Material Tracking")
page = st.sidebar.radio(
    "Select Module",
    ["Dashboard", "Concrete", "Rebar", "Mesh"]
)

# ============================================
# DASHBOARD PAGE
# ============================================

if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Get summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        concrete_summary = db.get_concrete_summary()
        st.metric(
            "Total Concrete",
            f"{concrete_summary.get('total_quantity_m3', 0):.1f} m³",
            delta=f"{concrete_summary.get('total_deliveries', 0)} deliveries"
        )
    
    with col2:
        rebar_summary = db.get_rebar_summary()
        st.metric(
            "Total Rebar",
            f"{rebar_summary.get('total_weight_kg', 0)/1000:.1f} tons",
            delta=f"{rebar_summary.get('total_deliveries', 0)} deliveries"
        )
    
    with col3:
        mesh_summary = db.get_mesh_summary()
        st.metric(
            "Total Mesh",
            f"{mesh_summary.get('total_weight_kg', 0)/1000:.1f} tons",
            delta=f"{mesh_summary.get('total_pieces', 0)} pieces"
        )
    
    # Charts
    st.markdown("### 📈 Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Concrete", "Rebar", "Mesh"])
    
    with tab1:
        # Concrete by location
        df_location = db.get_concrete_by_location()
        if not df_location.empty:
            st.bar_chart(df_location.set_index('location_block')['total_quantity_m3'])
        else:
            st.info("No concrete data available")
    
    with tab2:
        # Rebar by diameter
        df_diameter = db.get_rebar_by_diameter()
        if not df_diameter.empty:
            st.bar_chart(df_diameter.set_index('diameter')['total_kg'])
        else:
            st.info("No rebar data available")
    
    with tab3:
        # Mesh by type
        df_mesh_type = db.get_mesh_by_type()
        if not df_mesh_type.empty:
            st.dataframe(df_mesh_type, use_container_width=True)
        else:
            st.info("No mesh data available")

# ============================================
# CONCRETE PAGE
# ============================================

elif page == "Concrete":
    st.title("🚛 Concrete Management")
    
    # Add new concrete delivery
    with st.expander("➕ Add New Delivery", expanded=True):
        with st.form("concrete_form"):
            col1, col2, col3 = st.columns(3)
            
            date = col1.date_input("Date", datetime.now())
            supplier = col2.selectbox("Supplier", ["ÖZYURT BETON", "ALBAYRAK BETON", "OTHER"])
            waybill_no = col3.text_input("Waybill No")
            
            col4, col5, col6 = st.columns(3)
            
            concrete_class = col4.selectbox("Class", ["C16", "C20", "C25", "C30", "C35", "C40", "GRO", "ŞAP"])
            delivery_method = col5.selectbox("Method", ["POMPALI", "MİKSERLİ"])
            quantity = col6.number_input("Quantity (m³)", min_value=0.1, step=0.5)
            
            col7, col8 = st.columns(2)
            
            location_block = col7.text_input("Location/Block (e.g., GK1)")
            notes = col8.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                # Prepare data
                concrete_data = {
                    'date': date,
                    'supplier': supplier,
                    'waybill_no': waybill_no,
                    'concrete_class': concrete_class,
                    'delivery_method': delivery_method,
                    'quantity_m3': float(quantity),
                    'location_block': location_block if location_block else None,
                    'notes': notes if notes else None
                }
                
                # Save to database
                if db.add_concrete(concrete_data):
                    st.success("✅ Concrete record added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add record. Check logs for details.")
    
    # Display existing records
    st.markdown("### 📋 Delivery Records")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_supplier = st.selectbox("Filter by Supplier", ["All"] + db.get_all_suppliers())
    with col2:
        filter_start = st.date_input("From Date", value=None)
    with col3:
        filter_end = st.date_input("To Date", value=None)
    
    # Get filtered data
    df = db.get_concrete_logs(
        start_date=filter_start.isoformat() if filter_start else None,
        end_date=filter_end.isoformat() if filter_end else None,
        supplier=filter_supplier if filter_supplier != "All" else None
    )
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        st.info(f"📊 Total: {len(df)} records | {df['quantity_m3'].sum():.1f} m³")
    else:
        st.info("No records found. Add your first delivery above!")

# ============================================
# REBAR PAGE
# ============================================

elif page == "Rebar":
    st.title("⚙️ Rebar Management")
    
    # Add new rebar delivery
    with st.expander("➕ Add New Delivery", expanded=True):
        with st.form("rebar_form"):
            col1, col2, col3 = st.columns(3)
            
            date = col1.date_input("Date", datetime.now())
            supplier = col2.selectbox("Supplier", ["ŞAHİN DEMİR", "KARDEMİR", "İÇDAŞ", "OTHER"])
            waybill_no = col3.text_input("Waybill No")
            
            col4, col5 = st.columns(2)
            
            project_stage = col4.text_input("Project Stage (e.g., 3.ETAP)")
            manufacturer = col5.text_input("Manufacturer")
            
            st.markdown("##### Diameter Weights (kg)")
            
            # Create 3 rows of diameter inputs
            diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
            diameter_weights = {}
            
            for i in range(0, len(diameters), 4):
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    if i + j < len(diameters):
                        d = diameters[i + j]
                        diameter_weights[f'q{d}_kg'] = col.number_input(
                            f"Q{d}", 
                            min_value=0.0, 
                            step=100.0,
                            key=f"q{d}"
                        )
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                # Calculate total
                total_weight = sum(diameter_weights.values())
                
                # Prepare data
                rebar_data = {
                    'date': date,
                    'supplier': supplier,
                    'waybill_no': waybill_no,
                    'project_stage': project_stage if project_stage else None,
                    'manufacturer': manufacturer if manufacturer else None,
                    **diameter_weights,
                    'total_weight_kg': total_weight,
                    'notes': notes if notes else None
                }
                
                # Save to database
                if db.add_rebar(rebar_data):
                    st.success(f"✅ Rebar record added! Total: {total_weight:.0f} kg")
                    st.rerun()
                else:
                    st.error("❌ Failed to add record. Check logs for details.")
    
    # Display existing records
    st.markdown("### 📋 Delivery Records")
    
    df = db.get_rebar_logs()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        st.info(f"📊 Total: {len(df)} records | {df['total_weight_kg'].sum()/1000:.1f} tons")
    else:
        st.info("No records found. Add your first delivery above!")

# ============================================
# MESH PAGE
# ============================================

elif page == "Mesh":
    st.title("🕸️ Steel Mesh Management")
    
    # Add new mesh delivery
    with st.expander("➕ Add New Delivery", expanded=True):
        with st.form("mesh_form"):
            col1, col2, col3 = st.columns(3)
            
            date = col1.date_input("Date", datetime.now())
            supplier = col2.selectbox("Supplier", ["DOFER", "MUREL", "OTHER"])
            waybill_no = col3.text_input("Waybill No")
            
            col4, col5, col6 = st.columns(3)
            
            mesh_type = col4.selectbox("Type", ["Q", "R", "TR"])
            dimensions = col5.text_input("Dimensions (e.g., 215x500)")
            piece_count = col6.number_input("Piece Count", min_value=1, step=1)
            
            col7, col8 = st.columns(2)
            
            weight_kg = col7.number_input("Weight (kg)", min_value=0.1, step=10.0)
            usage_location = col8.text_input("Usage Location")
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Save Record")
            
            if submitted:
                # Prepare data
                mesh_data = {
                    'date': date,
                    'supplier': supplier,
                    'waybill_no': waybill_no,
                    'mesh_type': mesh_type,
                    'dimensions': dimensions if dimensions else None,
                    'piece_count': int(piece_count),
                    'weight_kg': float(weight_kg),
                    'usage_location': usage_location if usage_location else None,
                    'notes': notes if notes else None
                }
                
                # Save to database
                if db.add_mesh(mesh_data):
                    st.success("✅ Mesh record added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add record. Check logs for details.")
    
    # Display existing records
    st.markdown("### 📋 Delivery Records")
    
    df = db.get_mesh_logs()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        st.info(f"📊 Total: {len(df)} records | {df['piece_count'].sum()} pieces | {df['weight_kg'].sum()/1000:.1f} tons")
    else:
        st.info("No records found. Add your first delivery above!")

# ============================================
# FOOTER
# ============================================

st.sidebar.markdown("---")
st.sidebar.info("🚀 **Powered by Supabase**\nPostgreSQL Cloud Database")


