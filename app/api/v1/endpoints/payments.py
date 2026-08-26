import stripe
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.config import settings
from app.models.order import Order
from app.models.user import User

router = APIRouter()
stripe.api_key = settings.STRIPE_API_KEY

@router.post("/create-checkout-session/{order_id}")
async def create_checkout_session(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a Stripe Checkout Session for an order.
    """
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == current_user.id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order is already paid or cancelled")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'unit_amount': int(order.total_amount * 100),
                    'product_data': {
                        'name': f'Order #{str(order.id)[:8]}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://yourfrontend.com/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://yourfrontend.com/checkout/cancel",
            client_reference_id=str(order.id),
        )
        
        order.stripe_session_id = checkout_session.id
        db.add(order)
        await db.commit()
        
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(deps.get_db)):
    """
    Handle Stripe webhook events to update order status.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id_str = session.get('client_reference_id')
        payment_intent = session.get('payment_intent')
        
        if order_id_str:
            order_id = uuid.UUID(order_id_str)
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalars().first()
            
            if order:
                order.status = "paid"
                order.stripe_payment_intent = payment_intent
                db.add(order)
                await db.commit()

    return {"status": "success"}
