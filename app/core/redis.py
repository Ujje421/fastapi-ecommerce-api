import json
import uuid
from typing import Dict, Any, Optional
import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

class CartCache:
    """Handles cart operations in Redis."""
    
    PREFIX = "cart:"
    EXPIRATION = 60 * 60 * 24 * 7  # 7 days
    
    @classmethod
    def _key(cls, user_id: uuid.UUID) -> str:
        return f"{cls.PREFIX}{user_id}"
        
    @classmethod
    async def get_cart(cls, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get user cart from Redis."""
        key = cls._key(user_id)
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return {"user_id": str(user_id), "items": [], "total_amount": 0.0}
        
    @classmethod
    async def save_cart(cls, user_id: uuid.UUID, cart_data: Dict[str, Any]) -> None:
        """Save user cart to Redis."""
        key = cls._key(user_id)
        await redis_client.set(key, json.dumps(cart_data), ex=cls.EXPIRATION)
        
    @classmethod
    async def clear_cart(cls, user_id: uuid.UUID) -> None:
        """Clear user cart."""
        key = cls._key(user_id)
        await redis_client.delete(key)
