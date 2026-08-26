import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class CartItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    name: str
    price: float
    total: float
    
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    user_id: uuid.UUID
    items: List[CartItemResponse] = []
    total_amount: float = 0.0
