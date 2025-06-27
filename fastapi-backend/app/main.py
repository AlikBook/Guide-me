from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.data_loader import load_all_data  # ⬅️ lo veremos en el paso 2
from app.api.routes import router as api_router

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
    data = load_all_data()
    app.state.metro_data = data  

app.include_router(api_router)