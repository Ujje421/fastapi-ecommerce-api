from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.api import deps
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

router = APIRouter()

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get overview statistics for the admin dashboard.
    Only accessible by superusers.
    """
    # Total users
    users_result = await db.execute(select(func.count()).select_from(User))
    total_users = users_result.scalar()
    
    # Total revenue from paid orders
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(Order.status == "paid")
    )
    total_revenue = revenue_result.scalar() or 0.0
    
    # Total active products
    products_result = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )
    total_products = products_result.scalar()
    
    # Low stock alerts (products with < 10 stock)
    low_stock_result = await db.execute(
        select(Product).where(Product.stock_quantity < 10, Product.is_active == True)
    )
    low_stock_products = [
        {"id": p.id, "name": p.name, "stock": p.stock_quantity}
        for p in low_stock_result.scalars().all()
    ]
    
    return {
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_active_products": total_products,
        "low_stock_alerts": low_stock_products,
        "low_stock_count": len(low_stock_products),
    }
