from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

router = APIRouter(prefix="/api/sources", tags=["Sources"])

sources_db = [
    {"id": 1, "platform": "telegram", "name": "@sales_chat", "enabled": True, "last_scan": None},
    {"id": 2, "platform": "telegram", "name": "@buyers_chat", "enabled": True, "last_scan": None},
    {"id": 3, "platform": "reddit", "name": "r/askreddit", "enabled": False, "last_scan": None}
]
next_id = 4

@router.get("/")
async def get_sources():
    return {"sources": sources_db}

@router.post("/")
async def add_source(source: dict):
    global next_id
    new_source = {
        "id": next_id,
        "platform": source.get("platform", "telegram"),
        "name": source.get("name", ""),
        "enabled": source.get("enabled", True),
        "last_scan": None
    }
    sources_db.append(new_source)
    next_id += 1
    return {"status": "success", "source": new_source}

@router.put("/{source_id}")
async def update_source(source_id: int, source: dict):
    for s in sources_db:
        if s["id"] == source_id:
            if "name" in source:
                s["name"] = source["name"]
            if "enabled" in source:
                s["enabled"] = source["enabled"]
            if "platform" in source:
                s["platform"] = source["platform"]
            return {"status": "success", "source": s}
    raise HTTPException(status_code=404, detail="Source not found")

@router.delete("/{source_id}")
async def delete_source(source_id: int):
    for i, s in enumerate(sources_db):
        if s["id"] == source_id:
            sources_db.pop(i)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Source not found")
