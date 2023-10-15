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
        raise HTTPException(status_code=404, detail="No available items found for the specified shop")
    
    return available_items

@app.post("/add-review/{shop_id}/{item_id}")
async def add_review_to_item(
    shop_id: int,
    item_id: int,
    review: schemas.Review,  # Assuming you're using Pydantic schemas for request data
    db: Session = Depends(get_db)
):
    # Check if the item belongs to the specified shop
    item = db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.item_id == item_id).first()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found for the specified shop")
    
    # Assuming Review is a Pydantic model for request data, you can create a Review object
    new_review = models.Review(
        user_id=review.user_id,  # Set the user_id from the request data
        shop_id=shop_id,  # Use the shop_id from the URL
        created_at=review.created_at,  # Set created_at from the request data
        rating=review.rating,  # Set the rating from the request data
        comment=review.comment  # Set the comment from the request data
    )
    
    # Add the new review to the database
    db.add(new_review)
    db.commit()
    
    return new_review