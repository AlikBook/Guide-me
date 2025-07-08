from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.data_loader import load_all_data  # ⬅️ lo veremos en el paso 2
from app.api.routes import router as api_router
from app.core.auto_build import ensure_yen_wrapper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5173"] for Vite, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Paris Metro Assistant API"}

@app.on_event("startup")
def on_startup():
    import os
    # Set flag to indicate we're in startup context
    os.environ['FASTAPI_STARTUP'] = 'true'
    
    # Auto-build C extension if needed
    print("Checking C extension availability...")
    yen_available = ensure_yen_wrapper()
    
    if yen_available:
        print("High-performance mode enabled")
    else:
        print("Running in compatibility mode (slower performance)")
    
    # Load data
    data = load_all_data()
    app.state.metro_data = data
    app.state.yen_available = yen_available
    
    # Clear startup flag
    os.environ.pop('FASTAPI_STARTUP', None)

app.include_router(api_router)