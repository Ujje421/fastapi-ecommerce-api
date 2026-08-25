import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- Category Schemas ---

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    slug: str

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    slug: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: uuid.UUID
    slug: str
    
    model_config = ConfigDict(from_attributes=True)


# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int = 0
    is_active: bool = True
    category_id: uuid.UUID

class ProductCreate(ProductBase):
    slug: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[uuid.UUID] = None

class ProductResponse(ProductBase):
    id: uuid.UUID
    slug: str
    category: Optional[CategoryResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
