import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core.redis import CartCache
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new order from the user's current shopping cart.
    This reserves stock and clears the cart.
    """
    cart = await CartCache.get_cart(current_user.id)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Shopping cart is empty")
        
    # Create the order
    db_order = Order(
        user_id=current_user.id,
        status="pending",
        total_amount=cart["total_amount"],
        shipping_address=order_in.shipping_address,
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    # Verify stock and create OrderItems
    for item in cart["items"]:
        product_id = uuid.UUID(item["product_id"])
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        
        if not product or product.stock_quantity < item["quantity"]:
            # Rollback
            await db.delete(db_order)
            await db.commit()
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for product {item['name']}"
            )
            
        # Deduct stock
        product.stock_quantity -= item["quantity"]
        db.add(product)
        
        # Create order item
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item["quantity"],
            price_at_purchase=item["price"]
        )
        db.add(db_item)
        
    await db.commit()
    
    # Reload with items
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == db_order.id)
    )
    db_order = result.scalars().first()
    
    # Clear cart after successful order creation
    await CartCache.clear_cart(current_user.id)
    
    return db_order

@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve all orders for the current user."""
    query = select(Order).options(selectinload(Order.items)).where(Order.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a specific order by ID."""
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
        
    return order
