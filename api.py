from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse({
        "message": "?? MedTriageAI API is running on Vercel!",
        "status": "healthy",
        "version": "1.0.0"
    })

@app.get("/api/test")
async def test():
    return JSONResponse({
        "test": "success",
        "platform": "vercel"
    })