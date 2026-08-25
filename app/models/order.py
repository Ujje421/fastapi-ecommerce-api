import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class Order(Base):
    """Order model representing a customer's purchase."""
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), index=True)
    user: Mapped["User"] = relationship("User", back_populates="orders")
    
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, paid, shipped, delivered, cancelled
    total_amount: Mapped[float] = mapped_column(Float(), nullable=False)
    
    # Payment info
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    stripe_payment_intent: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Shipping info (simplified)
    shipping_address: Mapped[str] = mapped_column(String(500))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Line item in an order."""
    
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("order.id"), index=True)
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Float(), nullable=False)
