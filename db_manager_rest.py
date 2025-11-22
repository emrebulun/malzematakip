"""
Supabase Database Manager - REST API Version
Much more reliable than direct PostgreSQL connection!
"""

import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, date

class SupabaseManagerREST:
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
        """Bulk insert concrete records in batches"""
        try:
            total_inserted = 0
            failed = 0
            
            # Process in batches to avoid API limits
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                
                # Convert dates to strings
                for item in batch:
                    if isinstance(item.get('date'), (date, pd.Timestamp)):
                        item['date'] = item['date'].isoformat() if hasattr(item['date'], 'isoformat') else str(item['date'])
                
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
            
            # Set defaults for diameter fields
            for diameter in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
                data.setdefault(f'q{diameter}_kg', 0.0)
            
            response = self.client.table('rebar_logs').insert(data).execute()
            
            if response.data:
                st.success("✅ Rebar record added!")
                return True
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to add rebar: {e}")
            return False
    
    def get_rebar_logs(self,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """Get rebar delivery logs - ALL RECORDS using pagination"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                query = self.client.table('rebar_logs').select("*")
                
                if start_date:
                    query = query.gte('date', start_date)
                
                if end_date:
                    query = query.lte('date', end_date)
                
                response = query.order('date', desc=True).range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
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
            st.error(f"❌ Failed to get rebar logs: {e}")
            return pd.DataFrame()
    
    def get_rebar_summary(self) -> Dict:
        """Get rebar summary statistics - ALL RECORDS"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                response = self.client.table('rebar_logs').select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
                    if len(response.data) < page_size:
                        break
                    page += 1
                else:
                    break
            
            if all_data:
                df = pd.DataFrame(all_data)
                summary = {
                    'total_deliveries': len(df),
                    'total_weight_kg': df['total_weight_kg'].sum()
                }
                
                # Add per-diameter totals
                for diameter in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
                    col = f'q{diameter}_kg'
                    if col in df.columns:
                        summary[f'total_{col}'] = df[col].sum()
                
                return summary
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
    
    def get_mesh_logs(self,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """Get mesh delivery logs - ALL RECORDS using pagination"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                query = self.client.table('mesh_logs').select("*")
                
                if start_date:
                    query = query.gte('date', start_date)
                
                if end_date:
                    query = query.lte('date', end_date)
                
                response = query.order('date', desc=True).range(page * page_size, (page + 1) * page_size - 1).execute()
                
                if response.data:
                    all_data.extend(response.data)
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
            st.error(f"❌ Failed to get mesh logs: {e}")
            return pd.DataFrame()
    
    def get_mesh_summary(self) -> Dict:
        """Get mesh summary statistics - ALL RECORDS"""
        try:
            all_data = []
            page_size = 1000
            page = 0
            
            while True:
                response = self.client.table('mesh_logs').select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
                
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
                    'total_pieces': df['piece_count'].sum(),
                    'total_weight_kg': df['weight_kg'].sum(),
                    'type_count': df['mesh_type'].nunique()
                }
            return {}
            
        except Exception as e:
            st.error(f"❌ Failed to get mesh summary: {e}")
            return {}
    
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
def get_db_manager_rest() -> SupabaseManagerREST:
    """Get or create cached database manager instance (REST API)"""
    return SupabaseManagerREST()


