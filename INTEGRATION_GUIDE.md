# 🔗 Frontend-Backend Integration Guide

## Overview
The Streamlit frontend is now fully integrated with the FastAPI backend, providing a seamless full-stack experience.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Browser)                  │
│                  http://localhost:8501                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT FRONTEND (app.py)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Dark Corporate Industrial UI                       │  │
│  │  • Glassmorphism Design                              │  │
│  │  • Lottie Animations                                 │  │
│  │  • Interactive Charts (Plotly)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP Requests (api_client.py)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (main.py)                       │
│                  http://localhost:8000                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • RESTful API Endpoints                             │  │
│  │  • CRUD Operations                                   │  │
│  │  • Excel Import/Export                               │  │
│  │  • Analytics & Aggregations                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite DATABASE (malzeme.db)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • beton (Concrete)                                  │  │
│  │  • demir (Rebar)                                     │  │
│  │  • hasir (Mesh)                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. API Client (`api_client.py`)
Handles all communication between frontend and backend.

**Features:**
- Health check endpoint
- CRUD operations for all materials
- Excel import/export
- Analytics data fetching
- Automatic error handling
- Response caching

**Usage:**
```python
from api_client import get_api_client

api_client = get_api_client()
beton_data = api_client.get_all_beton()
```

### 2. Dual Mode Operation
The application supports two modes:

#### API Mode (Recommended)
- ✅ Backend server running
- ✅ Data persisted in database
- ✅ Full CRUD operations
- ✅ Excel import via API
- ✅ Advanced analytics

#### Local Mode (Fallback)
- ⚠️ Backend server offline
- ⚠️ Data in session state only
- ⚠️ Limited to manual entry
- ⚠️ No persistence between sessions

**Mode Detection:**
```python
if st.session_state.api_mode:
    # Use API
    api_client.create_beton(data)
else:
    # Use local session state
    st.session_state.beton_df = pd.concat([...])
```

## Setup Instructions

### Step 1: Start Backend Server

```bash
# Terminal 1 - Backend
cd C:\Users\emreb\Desktop\malzemastok
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend

```bash
# Terminal 2 - Frontend
cd C:\Users\emreb\Desktop\malzemastok
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Step 3: Verify Integration

1. Open browser to `http://localhost:8501`
2. Check sidebar for **"🟢 API Connected"** status
3. Try adding a new record
4. Verify data persists after page refresh

## API Endpoints Used

### Health Check
```
GET http://localhost:8000/health
```

### Concrete (Beton)
```
GET    /api/beton           # Get all records
POST   /api/beton           # Create new record
GET    /api/beton/{id}      # Get single record
PUT    /api/beton/{id}      # Update record
DELETE /api/beton/{id}      # Delete record
POST   /api/import/beton    # Import from Excel
```

### Rebar (Demir)
```
GET    /api/demir           # Get all records
POST   /api/demir           # Create new record
GET    /api/demir/{id}      # Get single record
PUT    /api/demir/{id}      # Update record
DELETE /api/demir/{id}      # Delete record
POST   /api/import/demir    # Import from Excel
```

### Mesh (Hasır)
```
GET    /api/hasir           # Get all records
POST   /api/hasir           # Create new record
GET    /api/hasir/{id}      # Get single record
PUT    /api/hasir/{id}      # Update record
DELETE /api/hasir/{id}      # Delete record
POST   /api/import/hasir    # Import from Excel
```

### Analytics
```
GET /api/analytics/dashboard        # Dashboard summary
GET /api/analytics/beton/by-date    # Concrete by date
GET /api/analytics/demir/by-date    # Rebar by date
GET /api/analytics/summary          # Overall summary
```

## Data Flow Examples

### Example 1: Adding New Concrete Record

**Frontend (app.py):**
```python
# User fills form and clicks "Save Record"
if submitted:
    if st.session_state.api_mode:
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
```

**API Client (api_client.py):**
```python
def create_beton(self, data: Dict) -> Dict:
    response = self.session.post(
        f"{self.base_url}/api/beton", 
        json=data
    )
    return self._handle_response(response)
```

**Backend (main.py):**
```python
@app.post("/api/beton", response_model=schemas.Beton)
def create_beton(beton: schemas.BetonCreate, db: Session = Depends(get_db)):
    db_beton = models.Beton(**beton.dict())
    db.add(db_beton)
    db.commit()
    db.refresh(db_beton)
    return db_beton
```

**Database (malzeme.db):**
```sql
INSERT INTO beton (tarih, firma, irsaliye_no, ...)
VALUES ('2024-11-21', 'ÖZYURT BETON', '12345', ...);
```

### Example 2: Excel Import

**Frontend:**
```python
uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
if uploaded_file:
    temp_path = "temp_beton.xlsx"
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    result = api_client.import_beton_excel(temp_path)
```

**API Client:**
```python
def import_beton_excel(self, file_path: str) -> Dict:
    with open(file_path, 'rb') as f:
        files = {'file': ('beton.xlsx', f, '...')}
        response = self.session.post(
            f"{self.base_url}/api/import/beton",
            files=files
        )
    return self._handle_response(response)
```

**Backend:**
```python
@app.post("/api/import/beton")
async def import_beton(file: UploadFile, db: Session = Depends(get_db)):
    df = pd.read_excel(file.file)
    # Process and map data
    for _, row in df.iterrows():
        db_beton = models.Beton(...)
        db.add(db_beton)
    db.commit()
    return {"count": len(df)}
```

## Error Handling

### Connection Errors
```python
if not api_client.health_check():
    st.warning("⚠️ Backend API is not available. Using local data mode.")
    load_initial_data_local()
```

### API Errors
```python
result = api_client.create_beton(data)
if 'error' in result:
    st.error(f"Failed to save: {result.get('error')}")
else:
    st.success("✅ Record added successfully!")
```

### Validation Errors
Backend uses Pydantic for automatic validation:
```python
class BetonCreate(BaseModel):
    tarih: date
    firma: str
    irsaliye_no: str
    miktar: float = Field(gt=0)  # Must be > 0
```

## Performance Optimizations

### 1. Caching
```python
@st.cache_resource
def get_api_client() -> APIClient:
    """Cached API client instance"""
    return APIClient()
```

### 2. Batch Operations
```python
# Import multiple records at once
result = api_client.import_beton_excel(file_path)
# Returns: {"count": 150, "success": true}
```

### 3. Lazy Loading
```python
# Only load data when needed
if st.session_state.beton_df.empty:
    beton_data = api_client.get_all_beton()
    st.session_state.beton_df = api_client.api_to_dataframe(beton_data, "beton")
```

## Security Considerations

### 1. CORS Configuration
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Input Validation
- Pydantic models validate all inputs
- SQL injection prevention via SQLAlchemy ORM
- File upload validation (type, size)

### 3. Error Messages
- User-friendly messages in frontend
- Detailed logs in backend
- No sensitive data exposure

## Troubleshooting

### Issue: "API not available" warning

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
python main.py
```

### Issue: "Failed to save" error

**Solution:**
1. Check backend logs for errors
2. Verify data format matches Pydantic schema
3. Check database permissions

### Issue: Excel import fails

**Solution:**
1. Verify Excel file format matches expected columns
2. Check backend logs for parsing errors
3. Ensure file is not corrupted

### Issue: Data not persisting

**Solution:**
1. Verify API mode is active (check sidebar)
2. Check database file exists: `malzeme.db`
3. Verify write permissions

## Testing

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend shows "API Connected"
- [ ] Can add new concrete record
- [ ] Can add new rebar record
- [ ] Can add new mesh record
- [ ] Excel import works
- [ ] Excel export works
- [ ] Data persists after refresh
- [ ] Charts display correctly
- [ ] Analytics update in real-time

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test get all beton
curl http://localhost:8000/api/beton

# Test analytics
curl http://localhost:8000/api/analytics/summary
```

## Migration from Local to API Mode

If you have existing data in local mode:

1. Export data to Excel from each module
2. Start backend server
3. Use Excel import feature to load data
4. Verify data in database
5. Continue using API mode

## Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Role-based access control
- [ ] Real-time updates (WebSockets)
- [ ] Offline mode with sync
- [ ] Mobile app integration
- [ ] Advanced reporting
- [ ] Data backup/restore

### API Improvements
- [ ] Pagination for large datasets
- [ ] Search and filtering
- [ ] Bulk operations
- [ ] Export to multiple formats
- [ ] Scheduled reports
- [ ] Email notifications

## Support

For issues or questions:
1. Check backend logs: `main.py` console output
2. Check frontend logs: Streamlit console
3. Review `API_README.md` for API documentation
4. Check `database_schema.sql` for database structure

---

**Version**: 2.0.0  
**Last Updated**: November 21, 2024  
**Integration Status**: ✅ Complete


