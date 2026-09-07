from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/modules", tags=["Modules"])

module_status = {
    "orchestrator": {"running": False, "pid": None, "last_activity": None},
    "client_search": {"running": False, "pid": None, "last_activity": None},
    "telegram_bot": {"running": False, "pid": None, "last_activity": None},
    "self_learning": {"running": False, "pid": None, "last_activity": None},
}

class ModuleAction(BaseModel):
    action: str

@router.get("/")
async def get_modules():
    return module_status

@router.post("/{module_name}")
async def control_module(module_name: str, action: ModuleAction):
    if module_name not in module_status:
        raise HTTPException(status_code=404, detail="Module not found")

    if action.action == "start":
        return await start_module(module_name)
    elif action.action == "stop":
        return await stop_module(module_name)
    elif action.action == "restart":
        await stop_module(module_name)
        return await start_module(module_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

async def start_module(module_name: str):
    if module_status[module_name]["running"]:
        return {"status": "already_running"}

    module_paths = {
        "orchestrator": "../orchestrator/main.py",
        "client_search": "../client_search/main.py",
        "telegram_bot": "../telegram_bot/main.py",
        "self_learning": "../self_learning/main.py",
    }
    script_path = module_paths.get(module_name)
    if not script_path or not os.path.exists(script_path):
        return {"status": "error", "message": f"Модуль {module_name} не найден"}

    try:
        process = subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else "."
        )
        module_status[module_name]["running"] = True
        module_status[module_name]["pid"] = process.pid
        module_status[module_name]["last_activity"] = datetime.now()
        return {"status": "started", "pid": process.pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def stop_module(module_name: str):
    if not module_status[module_name]["running"]:
        return {"status": "already_stopped"}
    pid = module_status[module_name]["pid"]
    if pid:
        try:
            import psutil
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
        except:
            pass
    module_status[module_name]["running"] = False
    module_status[module_name]["pid"] = None
    module_status[module_name]["last_activity"] = datetime.now()
    return {"status": "stopped"}
