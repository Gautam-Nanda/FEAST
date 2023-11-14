from pydantic import BaseModel
from datetime import datetime
from typing import List

class ReviewCreate(BaseModel):
    user_id: int
    shop_id: int
    item_id: int
    created_at: datetime
    rating: int
    comment: str


class Review(ReviewCreate):
    id: int = None


class ItemCreate(BaseModel):
    name: str
    veg_or_nonveg: str
    description: str
    price: int
    shop_id: int
    available: bool
    item_rating: float


class Item(ItemCreate):
    item_id: int

class OrderItem(BaseModel):
    item_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]
    total: int


# If you want to create a Pydantic model for an update operation (e.g., for updating an existing review or item), you can add an additional Pydantic model for updates.
