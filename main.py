from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import schemas
import models

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
    # Check if the item belongs to the specified shop
    item = crud.check_item_belongs_shop(db, shop_id, item_id)

    if item is None:
        raise HTTPException(
            status_code=404, detail="Item not found for the specified shop")

    # Assuming Review is a Pydantic model for request data, you can create a Review object
    new_review = crud.create_item_review(
        db, review.user_id, shop_id, item_id, review)

    return new_review


@app.get("/reviews/{shop_id}/{item_id}")
async def read_item_reviews(shop_id: int, item_id: int, db: Session = Depends(get_db)):
    item_reviews = crud.get_item_reviews(db, shop_id, item_id)

    if not item_reviews:
        raise HTTPException(
            status_code=404, detail="No available items found for the specified shop")

    return item_reviews
