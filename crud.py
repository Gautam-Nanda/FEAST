from sqlalchemy.orm import Session, joinedload
import models
from datetime import datetime, timedelta
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

def get_shop_reviews(db: Session, shop_id: int):
    # send reivewer name and item name as well
    return db.query(models.Review).filter(models.Review.shop_id == shop_id).options(joinedload(models.Review.reviewer), joinedload(models.Review.reviewed_item)).all()

def create_order(db: Session, user_id: int, shop_id: int, items: list, total: int):
    new_order = models.Order(
        user_id=user_id,
        shop_id=shop_id,
        total=total,
        status="PENDING",
        created_at=datetime.now()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item in items:
        new_order_item = models.OrderItem(
            order_id=new_order.id,
            item_id=item.item_id,
            quantity=item.quantity
        )
        db.add(new_order_item)
        db.commit()
    return {"order_id": new_order.id}

def get_store_id(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.item_id == item_id).first().shop_id

def get_store_orders(db: Session, shop_id: int):
    return db.query(models.Order).filter(models.Order.shop_id == shop_id).options(joinedload(models.Order.items).joinedload(models.OrderItem.item)).all()

def get_store_revenue(db: Session, shop_id: int):
    today = datetime.now()
    revenue_daily = db.query(models.Order).filter(models.Order.shop_id == shop_id, models.Order.created_at >= today).all()
    revenue_weekly = db.query(models.Order).filter(models.Order.shop_id == shop_id, models.Order.created_at >= today - timedelta(days=7)).all()
    revenue_monthly = db.query(models.Order).filter(models.Order.shop_id == shop_id, models.Order.created_at >= today - timedelta(days=30)).all()

    # return only numbers
    revenue_daily = sum([order.total for order in revenue_daily])
    revenue_weekly = sum([order.total for order in revenue_weekly])
    revenue_monthly = sum([order.total for order in revenue_monthly])

    return {"daily": revenue_daily, "weekly": revenue_weekly, "monthly": revenue_monthly}