from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter(requests_per_minute=100)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Çok fazla istek. Lütfen bir dakika bekleyin."}
        )
    
    response = await call_next(request)
    return response

# Request logging middleware
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Error handling
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Sunucu hatası oluştu",
            "error": str(exc)
        }
    )


