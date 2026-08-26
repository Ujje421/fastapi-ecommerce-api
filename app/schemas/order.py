import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# --- Order Item Schemas ---

class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int
    price_at_purchase: float

class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# --- Order Schemas ---

class OrderBase(BaseModel):
    shipping_address: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent: Optional[str] = None

class OrderResponse(OrderBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: float
    stripe_session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
