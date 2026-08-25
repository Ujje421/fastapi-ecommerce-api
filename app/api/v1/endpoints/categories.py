import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.product import Category
from app.models.user import User
from app.schemas.product import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve categories."""
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=CategoryResponse)
async def create_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new category. Only for superusers."""
    result = await db.execute(select(Category).where(Category.slug == category_in.slug))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Category with this slug already exists.")
        
    db_obj = Category(**category_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
