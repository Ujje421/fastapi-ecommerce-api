import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
) -> Any:
    """Retrieve products with optional filtering."""
    query = select(Product).options(selectinload(Product.category)).where(Product.is_active == True)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """Get product by ID."""
    result = await db.execute(
        select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new product. Only for superusers."""
    result = await db.execute(select(Product).where(Product.slug == product_in.slug))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Product with this slug already exists.")
        
    db_obj = Product(**product_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
