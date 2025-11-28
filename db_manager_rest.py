"""
Supabase Database Manager - REST API Version
Much more reliable than direct PostgreSQL connection!
"""

import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, date

class SupabaseManagerREST_v2:
    """
    Database manager using Supabase REST API
    More reliable than direct PostgreSQL connection
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Supabase via REST API"""
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["anon_key"]
            
            self.client = create_client(url, key)
            st.success("✅ Connected to Supabase via REST API")
            
        except Exception as e:
            st.error(f"❌ Failed to connect to Supabase: {e}")
            st.info("💡 Make sure .streamlit/secrets.toml has 'url' and 'anon_key'")
            raise
    
    # ============================================
    # CONCRETE OPERATIONS
    # ============================================
    
    def add_concrete(self, data: Dict) -> bool:
        """Add a new concrete delivery record"""
        try:
            # Convert date to string if needed
            if isinstance(data.get('date'), date):
                data['date'] = data['date'].isoformat()
            
            # Supabase automatically handles created_at/updated_at
            response = self.client.table('concrete_logs').insert(data).execute()
            
            if response.data:
                st.success("✅ Concrete record added!")
                return True
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to add concrete: {e}")
            return False
    
    def bulk_insert_concrete(self, data_list: List[Dict], batch_size: int = 500) -> Dict:
        """Bulk insert concrete records in batches with duplicate check"""
        try:
            if not data_list:
                return {'success': True, 'total_inserted': 0, 'failed': 0, 'skipped': 0, 'total_records': 0}

            # 1. Prepare data and find date range
            dates = []
            for item in data_list:
                if isinstance(item.get('date'), (date, pd.Timestamp)):
                    item['date'] = item['date'].isoformat() if hasattr(item['date'], 'isoformat') else str(item['date'])
                dates.append(item['date'])
            
            if not dates:
                return {'success': False, 'error': "No dates found in data"}

            min_date = min(dates)
            max_date = max(dates)

            # 2. Fetch existing records in this range to check for duplicates
            existing_logs = self.get_concrete_logs(start_date=min_date, end_date=max_date)
            
            existing_keys = set()
            if not existing_logs.empty:
                for _, row in existing_logs.iterrows():
                    # Normalize date to string YYYY-MM-DD
                    d_val = row['date']
                    if isinstance(d_val, pd.Timestamp):
                        d_str = d_val.strftime('%Y-%m-%d')
                    else:
                        d_str = str(d_val).split('T')[0]
                    
                    # Normalize supplier and waybill
                    supp = str(row['supplier']).strip().upper()
                    wayb = str(row['waybill_no']).strip().upper()
                    
                    key = (d_str, supp, wayb)
                    existing_keys.add(key)

            # 3. Filter duplicates
            new_data = []
            skipped = 0
            
            for item in data_list:
                # Normalize item date
                i_date = item['date']
                if 'T' in i_date: i_date = i_date.split('T')[0]
                
                i_supp = str(item['supplier']).strip().upper()
                i_wayb = str(item['waybill_no']).strip().upper()
                
                key = (i_date, i_supp, i_wayb)
                
                if key in existing_keys:
                    skipped += 1
                else:
                    new_data.append(item)
                    existing_keys.add(key) # Prevent duplicates within the batch

            if not new_data:
                return {
                    'success': True,
                    'total_inserted': 0,
                    'failed': 0,
                    'skipped': skipped,
                    'total_records': len(data_list),
                    'message': "All records were duplicates."
                }

            # 4. Insert new data in batches
            total_inserted = 0
            failed = 0
            
            for i in range(0, len(new_data), batch_size):
                batch = new_data[i:i + batch_size]
                try:
                    response = self.client.table('concrete_logs').insert(batch).execute()
                    if response.data:
                        total_inserted += len(response.data)
                except Exception as batch_error:
                    st.warning(f"⚠️ Batch {i//batch_size + 1} failed: {batch_error}")
                    failed += len(batch)
            
            return {
                'success': True,
                'total_inserted': total_inserted,
                'failed': failed,
                'skipped': skipped,
                'total_records': len(data_list)
            }
            
        except Exception as e:
            st.error(f"❌ Bulk insert failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_concrete_logs(self, 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None,
                          supplier: Optional[str] = None) -> pd.DataFrame:
        """Get concrete delivery logs with optional filters - ALL RECORDS using pagination"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                query = self.client.table('concrete_logs').select("*")
                
                if start_date:
                    query = query.gte('date', start_date)
                
                if end_date:
                    query = query.lte('date', end_date)
                
                if supplier:
                    query = query.eq('supplier', supplier)
                
                # Apply pagination
                response = query.order('date', desc=True).range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
                    
                    # If we got less than page_size records, we've reached the end
                    if len(response.data) < page_size:
                        break
                    
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Failed to get concrete logs: {e}")
            return pd.DataFrame()
    
    def get_concrete_summary(self) -> Dict:
        """Get concrete summary statistics - ALL RECORDS"""
        try:
            # Get all records with pagination
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                # Select only necessary columns to reduce payload
                response = self.client.table('concrete_logs').select("quantity_m3, supplier, location_block").range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size:
                        break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                return {
                    'total_deliveries': len(df),
                    'total_quantity_m3': df['quantity_m3'].sum(),
                    'supplier_count': df['supplier'].nunique(),
                    'location_count': df['location_block'].nunique()
                }
            return {}
            
        except Exception as e:
            st.error(f"❌ Failed to get summary: {e}")
            return {}
    
    def get_concrete_by_supplier(self) -> pd.DataFrame:
        """Get concrete grouped by supplier - ALL RECORDS"""
        try:
            # Get all records with pagination
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                response = self.client.table('concrete_logs').select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size:
                        break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                grouped = df.groupby(['supplier', 'concrete_class']).agg({
                    'id': 'count',
                    'quantity_m3': 'sum'
                }).reset_index()
                grouped.columns = ['supplier', 'concrete_class', 'delivery_count', 'total_quantity_m3']
                return grouped
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"❌ Failed to group by supplier: {e}")
            return pd.DataFrame()
    
    def get_concrete_by_location(self) -> pd.DataFrame:
        """Get concrete grouped by location - ALL RECORDS"""
        try:
            # Get all records with pagination
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                response = self.client.table('concrete_logs').select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size:
                        break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                df = df[df['location_block'].notna()]
                grouped = df.groupby('location_block').agg({
                    'id': 'count',
                    'quantity_m3': 'sum'
                }).reset_index()
                grouped.columns = ['location_block', 'delivery_count', 'total_quantity_m3']
                return grouped.sort_values('total_quantity_m3', ascending=False)
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"❌ Failed to group by location: {e}")
            return pd.DataFrame()

    # ============================================
    # REBAR OPERATIONS
    # ============================================

    def add_rebar(self, data: Dict) -> bool:
        """Add a new rebar delivery record"""
        try:
            if isinstance(data.get('date'), date):
                data['date'] = data['date'].isoformat()
            
            response = self.client.table('rebar_logs').insert(data).execute()
            
            if response.data:
                st.success("✅ Rebar record added!")
                return True
            return False
        except Exception as e:
            st.error(f"❌ Failed to add rebar: {e}")
            return False

    def bulk_insert_rebar(self, data_list: List[Dict], batch_size: int = 500) -> Dict:
        """Bulk insert rebar records in batches with duplicate check"""
        try:
            if not data_list:
                return {'success': True, 'total_inserted': 0, 'failed': 0, 'skipped': 0, 'total_records': 0}

            dates = []
            for item in data_list:
                if isinstance(item.get('date'), (date, pd.Timestamp)):
                    item['date'] = item['date'].isoformat() if hasattr(item['date'], 'isoformat') else str(item['date'])
                dates.append(item['date'])
            
            if not dates:
                return {'success': False, 'error': "No dates found in data"}

            min_date = min(dates)
            max_date = max(dates)

            existing_logs = self.get_rebar_logs(start_date=min_date, end_date=max_date)
            
            existing_keys = set()
            if not existing_logs.empty:
                for _, row in existing_logs.iterrows():
                    d_val = row['date']
                    if isinstance(d_val, pd.Timestamp):
                        d_str = d_val.strftime('%Y-%m-%d')
                    else:
                        d_str = str(d_val).split('T')[0]
                    
                    supp = str(row['supplier']).strip().upper()
                    # Rebar might use 'irsaliye_no' or 'waybill_no' depending on schema, assuming 'waybill_no' based on previous context or 'irsaliye_no'
                    # Checking previous context, rebar_columns mapped 'İrsaliye No' to 'waybill_no'.
                    # But wait, in add_rebar form in streamlit_app.py it uses 'irsaliye_no'. 
                    # Let's check the schema or usage. In excel_uploader it maps to 'waybill_no'.
                    # In streamlit_app.py add_rebar uses 'irsaliye_no'. This is inconsistent.
                    # However, for bulk insert we are using data from excel_uploader which uses 'waybill_no'.
                    # Let's assume the DB column is 'waybill_no' for consistency with concrete.
                    # If the DB column is 'irsaliye_no', then excel_uploader mapping is wrong or DB is different.
                    # Given I cannot check DB schema directly easily, I will support both keys for duplicate check.
                    
                    wayb = str(row.get('waybill_no') or row.get('irsaliye_no') or '').strip().upper()
                    
                    key = (d_str, supp, wayb)
                    existing_keys.add(key)

            new_data = []
            skipped = 0
            
            for item in data_list:
                i_date = item['date']
                if 'T' in i_date: i_date = i_date.split('T')[0]
                
                i_supp = str(item['supplier']).strip().upper()
                i_wayb = str(item.get('waybill_no') or item.get('irsaliye_no') or '').strip().upper()
                
                key = (i_date, i_supp, i_wayb)
                
                if key in existing_keys:
                    skipped += 1
                else:
                    new_data.append(item)
                    existing_keys.add(key)

            if not new_data:
                return {'success': True, 'total_inserted': 0, 'failed': 0, 'skipped': skipped, 'total_records': len(data_list), 'message': "All duplicates."}

            total_inserted = 0
            failed = 0
            
            for i in range(0, len(new_data), batch_size):
                batch = new_data[i:i + batch_size]
                try:
                    response = self.client.table('rebar_logs').insert(batch).execute()
                    if response.data:
                        total_inserted += len(response.data)
                except Exception as batch_error:
                    st.warning(f"⚠️ Batch {i//batch_size + 1} failed: {batch_error}")
                    failed += len(batch)
            
            return {'success': True, 'total_inserted': total_inserted, 'failed': failed, 'skipped': skipped, 'total_records': len(data_list)}
            
        except Exception as e:
            st.error(f"❌ Bulk insert rebar failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_rebar_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Get rebar logs"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            while True:
                query = self.client.table('rebar_logs').select("*")
                if start_date: query = query.gte('date', start_date)
                if end_date: query = query.lte('date', end_date)
                
                response = query.order('date', desc=True).range(page * page_size, (page + 1) * page_size - 1).execute()
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size: break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['date'] = pd.to_datetime(df['date'])
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Failed to get rebar logs: {e}")
            return pd.DataFrame()

    def get_rebar_summary(self) -> Dict:
        """Get rebar summary"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            while True:
                response = self.client.table('rebar_logs').select("total_weight_kg").range(page * page_size, (page + 1) * page_size - 1).execute()
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size: break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                return {
                    'total_deliveries': len(df),
                    'total_weight_kg': df['total_weight_kg'].sum()
                }
            return {}
        except Exception as e:
            st.error(f"❌ Failed to get rebar summary: {e}")
            return {}

    # ============================================
    # MESH OPERATIONS
    # ============================================

    def add_mesh(self, data: Dict) -> bool:
        """Add a new mesh delivery record"""
        try:
            if isinstance(data.get('date'), date):
                data['date'] = data['date'].isoformat()
            
            response = self.client.table('mesh_logs').insert(data).execute()
            if response.data:
                st.success("✅ Mesh record added!")
                return True
            return False
        except Exception as e:
            st.error(f"❌ Failed to add mesh: {e}")
            return False

    def bulk_insert_mesh(self, data_list: List[Dict], batch_size: int = 500) -> Dict:
        """Bulk insert mesh records"""
        try:
            if not data_list: return {'success': True, 'total_inserted': 0}

            dates = []
            for item in data_list:
                if isinstance(item.get('date'), (date, pd.Timestamp)):
                    item['date'] = item['date'].isoformat() if hasattr(item['date'], 'isoformat') else str(item['date'])
                dates.append(item['date'])
            
            if not dates: return {'success': False, 'error': "No dates"}

            min_date = min(dates)
            max_date = max(dates)

            existing_logs = self.get_mesh_logs(start_date=min_date, end_date=max_date)
            existing_keys = set()
            if not existing_logs.empty:
                for _, row in existing_logs.iterrows():
                    d_val = row['date']
                    d_str = d_val.strftime('%Y-%m-%d') if isinstance(d_val, pd.Timestamp) else str(d_val).split('T')[0]
                    supp = str(row['supplier']).strip().upper()
                    wayb = str(row['waybill_no']).strip().upper()
                    existing_keys.add((d_str, supp, wayb))

            new_data = []
            skipped = 0
            for item in data_list:
                i_date = item['date']
                if 'T' in i_date: i_date = i_date.split('T')[0]
                i_supp = str(item['supplier']).strip().upper()
                i_wayb = str(item['waybill_no']).strip().upper()
                
                if (i_date, i_supp, i_wayb) in existing_keys:
                    skipped += 1
                else:
                    new_data.append(item)
                    existing_keys.add((i_date, i_supp, i_wayb))

            if not new_data:
                return {'success': True, 'total_inserted': 0, 'skipped': skipped, 'message': "All duplicates"}

            total_inserted = 0
            failed = 0
            for i in range(0, len(new_data), batch_size):
                batch = new_data[i:i + batch_size]
                try:
                    response = self.client.table('mesh_logs').insert(batch).execute()
                    if response.data: total_inserted += len(response.data)
                except Exception as batch_error:
                    st.warning(f"⚠️ Batch failed: {batch_error}")
                    failed += len(batch)
            
            return {'success': True, 'total_inserted': total_inserted, 'failed': failed, 'skipped': skipped}

        except Exception as e:
            st.error(f"❌ Bulk insert mesh failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_mesh_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Get mesh logs"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            while True:
                query = self.client.table('mesh_logs').select("*")
                if start_date: query = query.gte('date', start_date)
                if end_date: query = query.lte('date', end_date)
                
                response = query.order('date', desc=True).range(page * page_size, (page + 1) * page_size - 1).execute()
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size: break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                df['date'] = pd.to_datetime(df['date'])
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Failed to get mesh logs: {e}")
            return pd.DataFrame()

    def get_mesh_summary(self) -> Dict:
        """Get mesh summary"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            while True:
                response = self.client.table('mesh_logs').select("weight_kg, mesh_type, supplier").range(page * page_size, (page + 1) * page_size - 1).execute()
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size: break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                return {
                    'total_deliveries': len(df),
                    'total_weight_kg': df['weight_kg'].sum(),
                    'type_count': df['mesh_type'].nunique()
                }
            return {}
        except Exception as e:
            st.error(f"❌ Failed to get mesh summary: {e}")
            return {}

    def delete_concrete_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, supplier: Optional[str] = None) -> Dict:
        """Delete concrete logs with filters"""
        try:
            query = self.client.table('concrete_logs').delete()
            
            filters_applied = False
            if start_date:
                query = query.gte('date', start_date)
                filters_applied = True
            if end_date:
                query = query.lte('date', end_date)
                filters_applied = True
            if supplier:
                query = query.eq('supplier', supplier)
                filters_applied = True
                
            # If no filters, delete all (using neq id trick)
            if not filters_applied:
                query = query.neq('id', '00000000-0000-0000-0000-000000000000')
                
            response = query.execute()
            return {'success': True, 'count': len(response.data) if response.data else 0}
            
        except Exception as e:
            st.error(f"❌ Silme işlemi başarısız: {e}")
            return {'success': False, 'error': str(e)}

    def delete_rebar_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, supplier: Optional[str] = None) -> Dict:
        """Delete rebar logs with filters"""
        try:
            query = self.client.table('rebar_logs').delete()
            
            filters_applied = False
            if start_date:
                query = query.gte('date', start_date)
                filters_applied = True
            if end_date:
                query = query.lte('date', end_date)
                filters_applied = True
            if supplier:
                query = query.eq('supplier', supplier)
                filters_applied = True
                
            if not filters_applied:
                query = query.neq('id', '00000000-0000-0000-0000-000000000000')
                
            response = query.execute()
            return {'success': True, 'count': len(response.data) if response.data else 0}
            
        except Exception as e:
            st.error(f"❌ Silme işlemi başarısız: {e}")
            return {'success': False, 'error': str(e)}

    def delete_mesh_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, supplier: Optional[str] = None) -> Dict:
        """Delete mesh logs with filters"""
        try:
            query = self.client.table('mesh_logs').delete()
            
            filters_applied = False
            if start_date:
                query = query.gte('date', start_date)
                filters_applied = True
            if end_date:
                query = query.lte('date', end_date)
                filters_applied = True
            if supplier:
                query = query.eq('supplier', supplier)
                filters_applied = True
                
            if not filters_applied:
                query = query.neq('id', '00000000-0000-0000-0000-000000000000')
                
            response = query.execute()
            return {'success': True, 'count': len(response.data) if response.data else 0}
            
        except Exception as e:
            st.error(f"❌ Silme işlemi başarısız: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================
    # UTILITY FUNCTIONS
    # ============================================
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Try to query any table
            response = self.client.table('concrete_logs').select("id").limit(1).execute()
            return True
        except:
            return False
    
    def get_all_suppliers(self) -> List[str]:
        """Get unique list of all suppliers - ALL RECORDS"""
        try:
            suppliers = set()
            
            # Get from concrete with pagination
            for table_name in ['concrete_logs', 'rebar_logs', 'mesh_logs']:
                page = 0
                page_size = 1000
                while True:
                    response = self.client.table(table_name).select("supplier").range(page * page_size, (page + 1) * page_size - 1).execute()
                    if response.data:
                        suppliers.update([r['supplier'] for r in response.data if r.get('supplier')])
                        if len(response.data) < page_size:
                            break
                        page += 1
                    else:
                        break
            
            return sorted(list(suppliers))
        except:
            return []


# ============================================
# CACHED INSTANCE
# ============================================

@st.cache_resource
def get_db_manager_rest_v5() -> SupabaseManagerREST_v2:
    """Get or create cached database manager instance (REST API) - V5"""
    print("Initializing SupabaseManagerREST_v2 (V5)...")
    return SupabaseManagerREST_v2()


