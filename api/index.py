# Vercel entry point - imports the main FastAPI app
from main import app

# Vercel will use this as the handler
handler = app