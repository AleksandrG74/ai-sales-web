from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter(prefix="/api/goals", tags=["Goals"])

class Goal(BaseModel):
    name: str
    description: str
    trigger_type: str
    trigger_value: str
    success_indicators: List[str]
    priority: int = 1

goals_db = [
    {"id": 1, "name": "Переход в каталог", "description": "Клиент перешел по ссылке на сайт с каталогом", "trigger_type": "link", "trigger_value": "https://example.com/catalog", "success_indicators": ["перешел", "открыл", "посмотрел", "по ссылке"], "priority": 2},
    {"id": 2, "name": "Оформление заказа", "description": "Клиент оформил заказ", "trigger_type": "keyword", "trigger_value": "заказываю, покупаю, беру, да", "success_indicators": ["купил", "заказал", "оплатил", "оформил"], "priority": 1},
    {"id": 3, "name": "Запись на консультацию", "description": "Клиент записался на консультацию", "trigger_type": "action", "trigger_value": "запись, консультация, встреча", "success_indicators": ["записался", "приду", "встретимся"], "priority": 3}
]
next_goal_id = 4

@router.get("/")
async def get_goals():
    return {"goals": goals_db}

@router.post("/")
async def add_goal(goal: Goal):
    global next_goal_id
    new_goal = goal.dict()
    new_goal["id"] = next_goal_id
    goals_db.append(new_goal)
    next_goal_id += 1
    return {"status": "success", "goal": new_goal}

@router.put("/{goal_id}")
async def update_goal(goal_id: int, goal: Goal):
    for g in goals_db:
        if g["id"] == goal_id:
            g["name"] = goal.name
            g["description"] = goal.description
            g["trigger_type"] = goal.trigger_type
            g["trigger_value"] = goal.trigger_value
            g["success_indicators"] = goal.success_indicators
            g["priority"] = goal.priority
            return {"status": "success", "goal": g}
    raise HTTPException(status_code=404, detail="Goal not found")

@router.delete("/{goal_id}")
async def delete_goal(goal_id: int):
    for i, g in enumerate(goals_db):
        if g["id"] == goal_id:
            goals_db.pop(i)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Goal not found")

@router.get("/detect/{message}")
async def detect_goal(message: str):
    results = []
    for goal in goals_db:
        for indicator in goal["success_indicators"]:
            if indicator.lower() in message.lower():
                results.append({
                    "goal": goal["name"],
                    "matched": indicator,
                    "confidence": 0.8,
                    "trigger_type": goal["trigger_type"],
                    "trigger_value": goal["trigger_value"]
                })
    if "http" in message or "://" in message:
        results.append({
            "goal": "Переход по ссылке",
            "matched": "link",
            "confidence": 1.0,
            "trigger_type": "link",
            "trigger_value": message
        })
    return {"detected_goals": results}
