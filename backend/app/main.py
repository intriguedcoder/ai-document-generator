from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, projects, generate, export, refinement
from app.utils.logger import setup_logger

# Setup logging
setup_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered document authoring and generation platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])
app.include_router(refinement.router, prefix="/api/refine", tags=["Refinement"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Document Generator API",
        "version": settings.APP_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
