from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1 import routes

settings =  get_settings()

app= FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered job applicatino assistant",
    version="1.0.0",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
     allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include API routes
app.include_router(routes.router,prefix=settings.API_V1_PREFIX,tags=["jobs"])

@app.get("/")
async def root():
    """Root endpoint"""
    return{
        "message":"Job Application AI API",
        "version":"1.0.0"
    }