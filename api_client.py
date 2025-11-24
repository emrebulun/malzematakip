"""
API Client for Construction Material Management System
Handles all communication between Streamlit frontend and FastAPI backend
"""

import requests
import pandas as pd
from typing import Optional, Dict, List, Any
import streamlit as st
from datetime import datetime
import io

class APIClient:
    """Client for interacting with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e}")
            return {"error": str(e)}
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return {"error": str(e)}
    
    # ============================================
    # HEALTH CHECK
    # ============================================
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    # ============================================
    # BETON (CONCRETE) ENDPOINTS
    # ============================================
    
    def get_all_beton(self) -> List[Dict]:
        """Get all concrete records"""
        try:
            response = self.session.get(f"{self.base_url}/api/beton")
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to fetch concrete data: {e}")
            return []
    
    def create_beton(self, data: Dict) -> Dict:
        """Create new concrete record"""
        try:
            # Convert date to string if needed
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.post(f"{self.base_url}/api/beton", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create concrete record: {e}")
            return {"error": str(e)}
    
    def update_beton(self, beton_id: int, data: Dict) -> Dict:
        """Update concrete record"""
        try:
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.put(f"{self.base_url}/api/beton/{beton_id}", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to update concrete record: {e}")
            return {"error": str(e)}
    
    def delete_beton(self, beton_id: int) -> bool:
        """Delete concrete record"""
        try:
            response = self.session.delete(f"{self.base_url}/api/beton/{beton_id}")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Failed to delete concrete record: {e}")
            return False
    
    def import_beton_excel(self, file_path: str) -> Dict:
        """Import concrete data from Excel"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': ('beton.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/import/beton", files=files)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to import concrete data: {e}")
            return {"error": str(e)}
    
    # ============================================
    # DEMIR (REBAR) ENDPOINTS
    # ============================================
    
    def get_all_demir(self) -> List[Dict]:
        """Get all rebar records"""
        try:
            response = self.session.get(f"{self.base_url}/api/demir")
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to fetch rebar data: {e}")
            return []
    
    def create_demir(self, data: Dict) -> Dict:
        """Create new rebar record"""
        try:
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.post(f"{self.base_url}/api/demir", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create rebar record: {e}")
            return {"error": str(e)}
    
    def update_demir(self, demir_id: int, data: Dict) -> Dict:
        """Update rebar record"""
        try:
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.put(f"{self.base_url}/api/demir/{demir_id}", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to update rebar record: {e}")
            return {"error": str(e)}
    
    def delete_demir(self, demir_id: int) -> bool:
        """Delete rebar record"""
        try:
            response = self.session.delete(f"{self.base_url}/api/demir/{demir_id}")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Failed to delete rebar record: {e}")
            return False
    
    def import_demir_excel(self, file_path: str) -> Dict:
        """Import rebar data from Excel"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': ('demir.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/import/demir", files=files)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to import rebar data: {e}")
            return {"error": str(e)}
    
    # ============================================
    # HASIR (MESH) ENDPOINTS
    # ============================================
    
    def get_all_hasir(self) -> List[Dict]:
        """Get all mesh records"""
        try:
            response = self.session.get(f"{self.base_url}/api/hasir")
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to fetch mesh data: {e}")
            return []
    
    def create_hasir(self, data: Dict) -> Dict:
        """Create new mesh record"""
        try:
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.post(f"{self.base_url}/api/hasir", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to create mesh record: {e}")
            return {"error": str(e)}
    
    def update_hasir(self, hasir_id: int, data: Dict) -> Dict:
        """Update mesh record"""
        try:
            if isinstance(data.get('tarih'), datetime):
                data['tarih'] = data['tarih'].isoformat()
            
            response = self.session.put(f"{self.base_url}/api/hasir/{hasir_id}", json=data)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to update mesh record: {e}")
            return {"error": str(e)}
    
    def delete_hasir(self, hasir_id: int) -> bool:
        """Delete mesh record"""
        try:
            response = self.session.delete(f"{self.base_url}/api/hasir/{hasir_id}")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Failed to delete mesh record: {e}")
            return False
    
    def import_hasir_excel(self, file_path: str) -> Dict:
        """Import mesh data from Excel"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': ('hasir.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = self.session.post(f"{self.base_url}/api/import/hasir", files=files)
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Failed to import mesh data: {e}")
            return {"error": str(e)}
    
    # ============================================
    # ANALYTICS ENDPOINTS
    # ============================================
    
    def get_dashboard_analytics(self) -> Dict:
        """Get dashboard analytics data"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/dashboard")
            return self._handle_response(response)
        except Exception as e:
            st.warning(f"Failed to fetch analytics: {e}")
            return {}
    
    def get_beton_by_date(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get concrete analytics by date range"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = self.session.get(f"{self.base_url}/api/analytics/beton/by-date", params=params)
            return self._handle_response(response)
        except Exception as e:
            st.warning(f"Failed to fetch concrete analytics: {e}")
            return {}
    
    def get_demir_by_date(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get rebar analytics by date range"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = self.session.get(f"{self.base_url}/api/analytics/demir/by-date", params=params)
            return self._handle_response(response)
        except Exception as e:
            st.warning(f"Failed to fetch rebar analytics: {e}")
            return {}
    
    def get_summary_analytics(self) -> Dict:
        """Get summary analytics"""
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/summary")
            return self._handle_response(response)
        except Exception as e:
            st.warning(f"Failed to fetch summary: {e}")
            return {}
    
    # ============================================
    # DATA CONVERSION HELPERS
    # ============================================
    
    def api_to_dataframe(self, data: List[Dict], data_type: str) -> pd.DataFrame:
        """Convert API response to DataFrame"""
        if not data:
            # Return empty DataFrame with appropriate columns
            if data_type == "beton":
                return pd.DataFrame(columns=[
                    'id', 'TARİH', 'FİRMA', 'İRSALİYE NO', 'BETON SINIFI', 
                    'TESLİM ŞEKLİ', 'MİKTAR (m3)', 'BLOK', 'AÇIKLAMA'
                ])
            elif data_type == "demir":
                cols = ['id', 'TARİH', 'ETAP', 'İRSALİYE NO', 'TEDARİKÇİ', 'ÜRETİCİ']
                caplar = [f"Q{i}" for i in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]]
                cols.extend(caplar)
                cols.append('TOPLAM AĞIRLIK (kg)')
                return pd.DataFrame(columns=cols)
            elif data_type == "hasir":
                return pd.DataFrame(columns=[
                    'id', 'TARİH', 'FİRMA', 'İRSALİYE NO', 'ETAP', 
                    'HASIR TİPİ', 'EBATLAR', 'ADET', 'AĞIRLIK (kg)', 'KULLANIM YERİ'
                ])
        
        df = pd.DataFrame(data)
        
        # Convert date strings to datetime
        if 'tarih' in df.columns:
            df['TARİH'] = pd.to_datetime(df['tarih'])
            df = df.drop('tarih', axis=1)
        
        # Rename columns based on data type
        if data_type == "beton":
            column_mapping = {
                'firma': 'FİRMA',
                'irsaliye_no': 'İRSALİYE NO',
                'beton_sinifi': 'BETON SINIFI',
                'teslim_sekli': 'TESLİM ŞEKLİ',
                'miktar': 'MİKTAR (m3)',
                'blok': 'BLOK',
                'aciklama': 'AÇIKLAMA'
            }
            df = df.rename(columns=column_mapping)
        
        elif data_type == "demir":
            column_mapping = {
                'etap': 'ETAP',
                'irsaliye_no': 'İRSALİYE NO',
                'tedarikci': 'TEDARİKÇİ',
                'uretici': 'ÜRETİCİ',
                'toplam_agirlik': 'TOPLAM AĞIRLIK (kg)'
            }
            # Add Q columns
            for i in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
                column_mapping[f'q{i}'] = f'Q{i}'
            
            df = df.rename(columns=column_mapping)
        
        elif data_type == "hasir":
            column_mapping = {
                'firma': 'FİRMA',
                'irsaliye_no': 'İRSALİYE NO',
                'etap': 'ETAP',
                'hasir_tipi': 'HASIR TİPİ',
                'ebatlar': 'EBATLAR',
                'adet': 'ADET',
                'agirlik': 'AĞIRLIK (kg)',
                'kullanim_yeri': 'KULLANIM YERİ'
            }
            df = df.rename(columns=column_mapping)
        
        return df


# Global API client instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get or create API client instance"""
    return APIClient()





