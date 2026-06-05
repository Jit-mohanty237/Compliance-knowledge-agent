import sys
from pathlib import Path

# Add backend directory to path to support clean absolute imports throughout the app
backend_root = Path(__file__).resolve().parent
if str(backend_root) not in sys.path:
    sys.path.append(str(backend_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.chat import router as chat_router

app = FastAPI(
    title="LATAM Compliance Agent API",
    description="API server providing RAG-augmented compliance query processing for Latin America.",
    version="1.0.0"
)

# CORS configuration - allow React dev server origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Route
@app.get("/health")
async def health_check():
    """
    Simple API health status probe.
    """
    return {
        "status": "healthy",
        "app": "LATAM Compliance Agent API"
    }

# Include chat router
app.include_router(chat_router, prefix="/api")
