from sqlalchemy.orm import Session
import models

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_shops(db:Session):
    return db.query(models.Shop).all()

def get_available_items_for_shop(db: Session, shop_id: int):
    return db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.available.is_(True)).all()