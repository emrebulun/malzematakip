"""
Supabase Database Manager for Construction Material Tracking System
Handles all database operations using SQLAlchemy and Streamlit connection
"""

import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, date
import uuid

class SupabaseManager:
    """
    Database manager for Supabase (PostgreSQL) operations
    Uses Streamlit's native connection or SQLAlchemy
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.engine = None
        self.Session = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Supabase using SQLAlchemy"""
        try:
            # Use SQLAlchemy with secrets (more reliable for Supabase)
            db_url = st.secrets["supabase"]["connection_string"]
            self.engine = create_engine(db_url, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            st.success("✅ Connected to Supabase via SQLAlchemy")
            
        except Exception as e:
            st.error(f"❌ Failed to connect to Supabase: {e}")
            st.info("💡 Make sure .streamlit/secrets.toml is configured correctly")
            st.info(f"🔍 Connection string: {db_url[:50]}..." if 'db_url' in locals() else "")
            raise
    
    def _execute_query(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Execute a SELECT query and return DataFrame"""
        try:
            # Use SQLAlchemy
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return pd.DataFrame()
    
    def _execute_insert(self, query: str, params: Dict) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        try:
            # Use SQLAlchemy
            with self.engine.begin() as connection:
                connection.execute(text(query), params)
            return True
        except Exception as e:
            st.error(f"Insert/Update failed: {e}")
            return False
    
    # ============================================
    # CONCRETE OPERATIONS
    # ============================================
    
    def add_concrete(self, data: Dict) -> bool:
        """
        Add a new concrete delivery record
        
        Args:
            data (Dict): {
                'date': date object or string,
                'supplier': str,
                'waybill_no': str,
                'concrete_class': str (C25, C30, etc.),
                'delivery_method': str (POMPALI, MİKSERLİ),
                'quantity_m3': float,
                'location_block': str (optional),
                'notes': str (optional)
            }
        
        Returns:
            bool: True if successful
        """
        query = """
        INSERT INTO concrete_logs 
            (date, supplier, waybill_no, concrete_class, delivery_method, 
             quantity_m3, location_block, notes)
        VALUES 
            (:date, :supplier, :waybill_no, :concrete_class, :delivery_method,
             :quantity_m3, :location_block, :notes)
        """
        
        # Convert date if needed
        if isinstance(data.get('date'), date):
            data['date'] = data['date'].isoformat()
        
        # Set defaults for optional fields
        data.setdefault('location_block', None)
        data.setdefault('notes', None)
        
        return self._execute_insert(query, data)
    
    def get_concrete_logs(self, 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None,
                          supplier: Optional[str] = None) -> pd.DataFrame:
        """
        Get concrete delivery logs with optional filters
        
        Args:
            start_date (str, optional): Filter from this date
            end_date (str, optional): Filter to this date
            supplier (str, optional): Filter by supplier
        
        Returns:
            pd.DataFrame: Concrete logs
        """
        query = "SELECT * FROM concrete_logs WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        if supplier:
            query += " AND supplier = :supplier"
            params['supplier'] = supplier
        
        query += " ORDER BY date DESC, created_at DESC"
        
        return self._execute_query(query, params)
    
    def get_concrete_summary(self) -> Dict:
        """Get concrete summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_deliveries,
            SUM(quantity_m3) as total_quantity_m3,
            COUNT(DISTINCT supplier) as supplier_count,
            COUNT(DISTINCT location_block) as location_count
        FROM concrete_logs
        """
        df = self._execute_query(query)
        return df.iloc[0].to_dict() if not df.empty else {}
    
    def get_concrete_by_supplier(self) -> pd.DataFrame:
        """Get concrete grouped by supplier"""
        query = """
        SELECT 
            supplier,
            concrete_class,
            COUNT(*) as delivery_count,
            SUM(quantity_m3) as total_quantity_m3
        FROM concrete_logs
        GROUP BY supplier, concrete_class
        ORDER BY supplier, concrete_class
        """
        return self._execute_query(query)
    
    def get_concrete_by_location(self) -> pd.DataFrame:
        """Get concrete grouped by location"""
        query = """
        SELECT 
            location_block,
            SUM(quantity_m3) as total_quantity_m3,
            COUNT(*) as delivery_count
        FROM concrete_logs
        WHERE location_block IS NOT NULL
        GROUP BY location_block
        ORDER BY total_quantity_m3 DESC
        """
        return self._execute_query(query)
    
    # ============================================
    # REBAR OPERATIONS
    # ============================================
    
    def add_rebar(self, data: Dict) -> bool:
        """
        Add a new rebar delivery record
        
        Args:
            data (Dict): {
                'date': date object or string,
                'supplier': str,
                'waybill_no': str,
                'project_stage': str (optional),
                'manufacturer': str (optional),
                'q8_kg': float (default 0),
                'q10_kg': float (default 0),
                ... (all diameter fields)
                'total_weight_kg': float (required)
            }
        
        Returns:
            bool: True if successful
        """
        query = """
        INSERT INTO rebar_logs 
            (date, supplier, waybill_no, project_stage, manufacturer,
             q8_kg, q10_kg, q12_kg, q14_kg, q16_kg, q18_kg, 
             q20_kg, q22_kg, q25_kg, q28_kg, q32_kg, 
             total_weight_kg, notes)
        VALUES 
            (:date, :supplier, :waybill_no, :project_stage, :manufacturer,
             :q8_kg, :q10_kg, :q12_kg, :q14_kg, :q16_kg, :q18_kg,
             :q20_kg, :q22_kg, :q25_kg, :q28_kg, :q32_kg,
             :total_weight_kg, :notes)
        """
        
        # Convert date if needed
        if isinstance(data.get('date'), date):
            data['date'] = data['date'].isoformat()
        
        # Set defaults for optional fields
        data.setdefault('project_stage', None)
        data.setdefault('manufacturer', None)
        data.setdefault('notes', None)
        
        # Set default 0 for all diameter fields
        for diameter in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
            data.setdefault(f'q{diameter}_kg', 0.0)
        
        # Calculate total if not provided
        if 'total_weight_kg' not in data:
            data['total_weight_kg'] = sum(
                data.get(f'q{d}_kg', 0) for d in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
            )
        
        return self._execute_insert(query, data)
    
    def get_rebar_logs(self,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       supplier: Optional[str] = None) -> pd.DataFrame:
        """Get rebar delivery logs with optional filters"""
        query = "SELECT * FROM rebar_logs WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        if supplier:
            query += " AND supplier = :supplier"
            params['supplier'] = supplier
        
        query += " ORDER BY date DESC, created_at DESC"
        
        return self._execute_query(query, params)
    
    def get_rebar_summary(self) -> Dict:
        """Get rebar summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_deliveries,
            SUM(total_weight_kg) as total_weight_kg,
            SUM(q8_kg) as total_q8_kg,
            SUM(q10_kg) as total_q10_kg,
            SUM(q12_kg) as total_q12_kg,
            SUM(q14_kg) as total_q14_kg,
            SUM(q16_kg) as total_q16_kg,
            SUM(q18_kg) as total_q18_kg,
            SUM(q20_kg) as total_q20_kg,
            SUM(q22_kg) as total_q22_kg,
            SUM(q25_kg) as total_q25_kg,
            SUM(q28_kg) as total_q28_kg,
            SUM(q32_kg) as total_q32_kg
        FROM rebar_logs
        """
        df = self._execute_query(query)
        return df.iloc[0].to_dict() if not df.empty else {}
    
    def get_rebar_by_diameter(self) -> pd.DataFrame:
        """Get rebar totals by diameter"""
        query = """
        SELECT 
            'Q8' as diameter, SUM(q8_kg) as total_kg FROM rebar_logs
        UNION ALL SELECT 'Q10', SUM(q10_kg) FROM rebar_logs
        UNION ALL SELECT 'Q12', SUM(q12_kg) FROM rebar_logs
        UNION ALL SELECT 'Q14', SUM(q14_kg) FROM rebar_logs
        UNION ALL SELECT 'Q16', SUM(q16_kg) FROM rebar_logs
        UNION ALL SELECT 'Q18', SUM(q18_kg) FROM rebar_logs
        UNION ALL SELECT 'Q20', SUM(q20_kg) FROM rebar_logs
        UNION ALL SELECT 'Q22', SUM(q22_kg) FROM rebar_logs
        UNION ALL SELECT 'Q25', SUM(q25_kg) FROM rebar_logs
        UNION ALL SELECT 'Q28', SUM(q28_kg) FROM rebar_logs
        UNION ALL SELECT 'Q32', SUM(q32_kg) FROM rebar_logs
        ORDER BY diameter
        """
        return self._execute_query(query)
    
    # ============================================
    # MESH OPERATIONS
    # ============================================
    
    def add_mesh(self, data: Dict) -> bool:
        """
        Add a new mesh delivery record
        
        Args:
            data (Dict): {
                'date': date object or string,
                'supplier': str,
                'waybill_no': str,
                'mesh_type': str (Q, R, TR),
                'dimensions': str (optional),
                'piece_count': int,
                'weight_kg': float,
                'usage_location': str (optional),
                'notes': str (optional)
            }
        
        Returns:
            bool: True if successful
        """
        query = """
        INSERT INTO mesh_logs 
            (date, supplier, waybill_no, mesh_type, dimensions,
             piece_count, weight_kg, usage_location, notes)
        VALUES 
            (:date, :supplier, :waybill_no, :mesh_type, :dimensions,
             :piece_count, :weight_kg, :usage_location, :notes)
        """
        
        # Convert date if needed
        if isinstance(data.get('date'), date):
            data['date'] = data['date'].isoformat()
        
        # Set defaults for optional fields
        data.setdefault('dimensions', None)
        data.setdefault('usage_location', None)
        data.setdefault('notes', None)
        
        return self._execute_insert(query, data)
    
    def get_mesh_logs(self,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      supplier: Optional[str] = None) -> pd.DataFrame:
        """Get mesh delivery logs with optional filters"""
        query = "SELECT * FROM mesh_logs WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        if supplier:
            query += " AND supplier = :supplier"
            params['supplier'] = supplier
        
        query += " ORDER BY date DESC, created_at DESC"
        
        return self._execute_query(query, params)
    
    def get_mesh_summary(self) -> Dict:
        """Get mesh summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_deliveries,
            SUM(piece_count) as total_pieces,
            SUM(weight_kg) as total_weight_kg,
            COUNT(DISTINCT mesh_type) as type_count
        FROM mesh_logs
        """
        df = self._execute_query(query)
        return df.iloc[0].to_dict() if not df.empty else {}
    
    def get_mesh_by_type(self) -> pd.DataFrame:
        """Get mesh grouped by type"""
        query = """
        SELECT 
            mesh_type,
            COUNT(*) as delivery_count,
            SUM(piece_count) as total_pieces,
            SUM(weight_kg) as total_weight_kg
        FROM mesh_logs
        GROUP BY mesh_type
        ORDER BY mesh_type
        """
        return self._execute_query(query)
    
    # ============================================
    # UTILITY FUNCTIONS
    # ============================================
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            query = "SELECT 1 as test"
            result = self._execute_query(query)
            return not result.empty
        except:
            return False
    
    def get_all_suppliers(self) -> List[str]:
        """Get unique list of all suppliers"""
        query = """
        SELECT DISTINCT supplier FROM (
            SELECT supplier FROM concrete_logs
            UNION
            SELECT supplier FROM rebar_logs
            UNION
            SELECT supplier FROM mesh_logs
        ) AS all_suppliers
        ORDER BY supplier
        """
        df = self._execute_query(query)
        return df['supplier'].tolist() if not df.empty else []


# ============================================
# CACHED INSTANCE
# ============================================

@st.cache_resource
def get_db_manager() -> SupabaseManager:
    """Get or create cached database manager instance"""
    return SupabaseManager()

