import sys
from pathlib import Path

# Add backend directory to path to support clean absolute imports throughout the app
backend_root = Path(__file__).resolve().parent
if str(backend_root) not in sys.path:
    sys.path.append(str(backend_root))

from routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager
from vector_db.retriever import init_chroma
from compliance_agent import init_agents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eagerly pre-initialize Chroma client, embedding function, and collections on startup
    init_chroma()
    # Eagerly pre-initialize LLMs and agents on startup
    init_agents()
    yield

app = FastAPI(
    title="LATAM Compliance Agent API",
    description="API server providing RAG-augmented compliance query processing for Latin America.",
    version="1.0.0",
    lifespan=lifespan
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

# Startup diagnostics
print("[DEBUG] Loaded IntentClassifier")
print("[DEBUG] Loaded Knowledge Bases")
print("[DEBUG] COMPLIANCE Collection: latam_compliance")
print("[DEBUG] HR Collection: hr_playbook")
