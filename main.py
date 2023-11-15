from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import schemas
from typing import Optional

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/shops")
async def get_shops(db: Session = Depends(get_db)):
    shops = crud.get_shops(db)
    if not shops:
        raise HTTPException(status_code=404, detail="No shops found")
    return shops


@app.get("/available-items/{shop_id}")
async def read_available_items_for_shop(shop_id: int, db: Session = Depends(get_db)):
    available_items = crud.get_available_items_for_shop(db, shop_id)

    if not available_items:
        raise HTTPException(
            status_code=404, detail="No available items found for the specified shop")

    return available_items


@app.post("/add-review/{shop_id}/{item_id}")
async def add_review_to_item(
    shop_id: int,
    item_id: int,
    review: schemas.Review,  # Assuming you're using Pydantic schemas for request data
    db: Session = Depends(get_db)
):
    print(review)
    # Check if the item belongs to the specified shop
    item = crud.check_item_belongs_shop(db, shop_id, item_id)

    if item is None:
        raise HTTPException(
            status_code=404, detail="Item not found for the specified shop")

    # Assuming Review is a Pydantic model for request data, you can create a Review object
    new_review = crud.create_item_review(
        db, review.user_id, shop_id, item_id, review)

    # get avg rating of item and number of reviews
    # total_rating = avg_rating * num_reviews
    # update avg rating of item
    # avg_rating = (total_rating + new_review.rating) / (num_reviews + 1)
    # update num_reviews of item
    # num_reviews += 1

    return new_review


@app.get("/reviews/{shop_id}/{item_id}")
async def read_item_reviews(shop_id: int, item_id: int, db: Session = Depends(get_db)):
    item_reviews = crud.get_item_reviews(db, shop_id, item_id)

    if not item_reviews:
        raise HTTPException(
            status_code=404, detail="No available reviews found for the specified item")

    return item_reviews


@app.get("/reviews/{shop_id}")
async def read_shop_reviews(shop_id: int, db: Session = Depends(get_db)):
    shop_reviews = crud.get_shop_reviews(db, shop_id)

    if not shop_reviews:
        raise HTTPException(
            status_code=404, detail="No available reviews found for the specified shop")

    return shop_reviews


@app.get("/orders/store/{store_id}")
async def get_store_orders(store_id: int, limit: Optional[int] = 3, type: Optional[str] = "ALL", db: Session = Depends(get_db)):
    orders = crud.get_store_orders(db, store_id, limit=limit, type=type)

    if not orders:
        raise HTTPException(
            status_code=404, detail="No available orders found for the specified store")

    return orders


@app.post("/orders/create")
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # get store id from item id
    print(order)
    store_id = crud.get_store_id(db, order.items[0].item_id)
    new_order = crud.create_order(
        db, order.user_id, store_id, order.items, order.total)

    return new_order

# now create a app.get which fetches all the orders


@app.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    orders = crud.get_orders(db)

    if not orders:
        raise HTTPException(
            status_code=404, detail="No orders found")

    store_orders = {}
    for order in orders:
        if order.order_id not in store_orders:
            store_orders[order.order_id] = {
                "shop_id": order.item.shop_id,  # Access shop_id through item
                "items": [],
                "total": 0  # Initialize total
            }
        store_orders[order.order_id]["items"].append({
            "item_id": order.item_id,
            "quantity": order.quantity
        })
        # Add the price of the current item to the total
        store_orders[order.order_id]["total"] += order.item.price * order.quantity

    for order_id in store_orders:
        store_orders[order_id]["store_name"] = crud.get_store_name(
            db, store_orders[order_id]["shop_id"])
        for item in store_orders[order_id]["items"]:
            item["item_name"] = crud.get_item_names(db, item["item_id"])

    return store_orders


@app.get("/store/{store_id}/revenue-stats")
async def get_store_revenue(store_id: int, db: Session = Depends(get_db)):
    revenue = crud.get_store_revenue(db, store_id)

    if not revenue:
        raise HTTPException(
            status_code=404, detail="No revenue found for the specified store")

    return revenue


@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = crud.update_order_status(db, order_id, status)

    if not order:
        raise HTTPException(
            status_code=404, detail="No order found for the specified order id")

    return order


@app.get("/store/{store_id}/items")
async def get_store_items(store_id: int, db: Session = Depends(get_db)):
    items = crud.get_store_items(db, store_id)

    if not items:
        raise HTTPException(
            status_code=404, detail="No items found for the specified store")

    return items