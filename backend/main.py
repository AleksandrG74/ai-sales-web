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
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER", "admin"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASS", "changeme"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


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

@app.get("/", dependencies=[Depends(check_auth)])
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Sales Agent API", "docs": "/docs"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Sales Agent"}



@app.get("/api/database/download")
async def download_db():
    db_path = "/app/backend/data/database.db"
    if not os.path.exists(db_path):
        return {"error": "Database not found", "path": db_path}
    return FileResponse(
        db_path,
        media_type="application/octet-stream",
        filename="ai_sales_database.db"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
