import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class Category(Base):
    """Product category model."""
    
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    """E-commerce product model."""
    
    name: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text())
    price: Mapped[float] = mapped_column(Float(), nullable=False)
    
    # Inventory
    stock_quantity: Mapped[int] = mapped_column(Integer(), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
