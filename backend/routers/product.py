from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, ProductConfigDB
from models import ProductConfig

router = APIRouter(prefix="/api/product", tags=["Product"])

@router.get("/")
async def get_product_config(db: Session = Depends(get_db)):
    config = db.query(ProductConfigDB).first()
    if not config:
        return None
    return {
        "id": config.id,
        "name": config.name,
        "category": config.category,
        "attributes": json.loads(config.attributes) if config.attributes else [],
        "keywords": json.loads(config.keywords) if config.keywords else [],
        "industries": json.loads(config.industries) if config.industries else [],
        "regions": json.loads(config.regions) if config.regions else [],
        "updated_at": config.updated_at.isoformat() if config.updated_at else None
    }

@router.post("/")
async def update_product_config(config: ProductConfig, db: Session = Depends(get_db)):
    existing = db.query(ProductConfigDB).first()
    if existing:
        existing.name = config.name
        existing.category = config.category
        existing.attributes = json.dumps(config.attributes)
        existing.keywords = json.dumps(config.keywords)
        existing.industries = json.dumps(config.industries)
        existing.regions = json.dumps(config.regions)
    else:
        existing = ProductConfigDB(
            name=config.name,
            category=config.category,
            attributes=json.dumps(config.attributes),
            keywords=json.dumps(config.keywords),
            industries=json.dumps(config.industries),
            regions=json.dumps(config.regions)
        )
        db.add(existing)
    db.commit()
    return {"status": "success", "message": "Конфигурация сохранена"}
