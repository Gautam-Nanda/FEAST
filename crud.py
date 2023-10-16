from sqlalchemy.orm import Session
import models
from schemas import ReviewCreate


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_shops(db: Session):
    return db.query(models.Shop).all()


def get_available_items_for_shop(db: Session, shop_id: int):
    return db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.available.is_(True)).all()


def check_item_belongs_shop(db: Session, shop_id: int, item_id: int):
    return db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.item_id == item_id).first()


def create_item_review(db: Session, user_id: int, shop_id: int,item_id:int, new_review_data: ReviewCreate):
    new_review = models.Review(
        user_id=user_id,
        shop_id=shop_id,
        item_id=item_id,
        created_at=new_review_data.created_at,
        rating=new_review_data.rating,
        comment=new_review_data.comment
    )
    db.add(new_review)
    db.commit()
    return new_review


def get_item_reviews(db: Session, shop_id: int, item_id: int):
    return db.query(models.Review).filter(models.Item.shop_id == shop_id, models.Review.item_id == item_id).all()
