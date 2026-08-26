import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.redis import CartCache
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse

router = APIRouter()

@router.get("/", response_model=CartResponse)
async def get_cart(current_user: User = Depends(deps.get_current_user)) -> dict:
    """Retrieve current user's shopping cart."""
    return await CartCache.get_cart(current_user.id)

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    *,
    db: AsyncSession = Depends(deps.get_db),
    item_in: CartItemCreate,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """Add item to cart or update quantity if it already exists."""
    # Verify product exists and is active
    result = await db.execute(select(Product).where(Product.id == item_in.product_id))
    product = result.scalars().first()
    
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found or inactive")
        
    if product.stock_quantity < item_in.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    cart = await CartCache.get_cart(current_user.id)
    
    # Check if item exists in cart
    existing_item_idx = next(
        (i for i, item in enumerate(cart["items"]) if item["product_id"] == str(item_in.product_id)), 
        None
    )
    
    if existing_item_idx is not None:
        new_quantity = cart["items"][existing_item_idx]["quantity"] + item_in.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        cart["items"][existing_item_idx]["quantity"] = new_quantity
        cart["items"][existing_item_idx]["total"] = new_quantity * product.price
    else:
        cart["items"].append({
            "product_id": str(product.id),
            "name": product.name,
            "price": product.price,
            "quantity": item_in.quantity,
            "total": item_in.quantity * product.price
        })
        
    # Recalculate total
    cart["total_amount"] = sum(item["total"] for item in cart["items"])
    
    await CartCache.save_cart(current_user.id, cart)
    return cart

@router.put("/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: uuid.UUID,
    item_in: CartItemUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """Update cart item quantity."""
    cart = await CartCache.get_cart(current_user.id)
    
    existing_item_idx = next(
        (i for i, item in enumerate(cart["items"]) if item["product_id"] == str(product_id)), 
        None
    )
    
    if existing_item_idx is None:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    if item_in.quantity <= 0:
        cart["items"].pop(existing_item_idx)
    else:
        # Check stock
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if not product or product.stock_quantity < item_in.quantity:
             raise HTTPException(status_code=400, detail="Insufficient stock")
             
        cart["items"][existing_item_idx]["quantity"] = item_in.quantity
        cart["items"][existing_item_idx]["total"] = item_in.quantity * cart["items"][existing_item_idx]["price"]
        
    cart["total_amount"] = sum(item["total"] for item in cart["items"])
    await CartCache.save_cart(current_user.id, cart)
    return cart

@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_cart_item(
    product_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """Remove item from cart completely."""
    cart = await CartCache.get_cart(current_user.id)
    
    cart["items"] = [item for item in cart["items"] if item["product_id"] != str(product_id)]
    cart["total_amount"] = sum(item["total"] for item in cart["items"])
    
    await CartCache.save_cart(current_user.id, cart)
    return cart

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(current_user: User = Depends(deps.get_current_user)):
    """Clear the entire cart."""
    await CartCache.clear_cart(current_user.id)
