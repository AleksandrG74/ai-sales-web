# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import leads, product, intents, modules, logs, sources, settings, goals, orchestrator, web_search
from database import init_db

init_db()

app = FastAPI(title="AI Sales Agent", version="1.0.0")

# Подключаем все роутеры
app.include_router(leads.router)
app.include_router(product.router)
app.include_router(intents.router)
app.include_router(modules.router)
app.include_router(logs.router)
app.include_router(sources.router)
app.include_router(settings.router)
app.include_router(goals.router)
app.include_router(orchestrator.router)
app.include_router(web_search.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Sales Agent API", "docs": "/docs"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Sales Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
