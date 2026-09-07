from fastapi import APIRouter, Query, HTTPException
import os

router = APIRouter(prefix="/api/logs", tags=["Logs"])

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

@router.get("/")
async def get_log(
    module: str = Query("orchestrator"),
    lines: int = Query(100)
):
    log_files = {
        "orchestrator": "orchestrator.log",
        "client_search": "search.log",
        "telegram_bot": "telegram.log",
        "classifier": "classifier.log",
        "self_learning": "learning.log",
    }
    filename = log_files.get(module)
    if not filename:
        raise HTTPException(status_code=400, detail="Unknown module")

    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return f"Лог-файл {filename} не найден"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines_list = content.split("\n")
            last_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list
            return "\n".join(last_lines)
    except Exception as e:
        return f"Ошибка чтения лога: {str(e)}"
