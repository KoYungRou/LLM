from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import endpoint modules
from endpoints.select_pdfcontent import router as select_router
from endpoints.upload_pdf import router as upload_router
from endpoints.summarize import router as summarize_router
from endpoints.ask_question import router as question_router

# Create the FastAPI app
app = FastAPI(
    title="PDF AI Assistant API",
    description="API for PDF processing and LLM integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(select_router)
app.include_router(upload_router)
app.include_router(summarize_router)
app.include_router(question_router)

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "PDF AI Assistant API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)