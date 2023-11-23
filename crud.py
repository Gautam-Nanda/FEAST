from database import Base
from sqlalchemy.orm import Session, joinedload
import models
from datetime import datetime, timedelta
from schemas import ReviewCreate, ItemCreate


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_shops(db: Session):
    return db.query(models.Shop).all()


def get_available_items_for_shop(db: Session, shop_id: int):
    return db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.available.is_(True)).all()


def check_item_belongs_shop(db: Session, shop_id: int, item_id: int):
    return db.query(models.Item).filter(models.Item.shop_id == shop_id, models.Item.item_id == item_id).first()


def create_item_review(db: Session, user_id: int, shop_id: int, item_id: int, new_review_data: ReviewCreate):
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
            quantity=item.quantity,
            total=total
        )
        db.add(new_order_item)
        db.commit()
    return {"order_id": new_order.id}


def get_store_name(db: Session, shop_id: int):
    return db.query(models.Shop).filter(models.Shop.shop_id == shop_id).first().name


def get_item_names(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.item_id == item_id).first().name


def get_orders(db: Session):
    return db.query(models.OrderItem).all()


def get_store_id(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.item_id == item_id).first().shop_id


def get_store_orders(db: Session, shop_id: int, limit: int, type: str):
    if type == "ALL":
        return db.query(models.Order).filter(models.Order.shop_id == shop_id).options(joinedload(models.Order.items).joinedload(models.OrderItem.item)).limit(limit).all()
    return db.query(models.Order).filter(models.Order.shop_id == shop_id).filter(models.Order.status == type).options(joinedload(models.Order.items).joinedload(models.OrderItem.item)).limit(limit).all()


def get_store_revenue(db: Session, shop_id: int):
    today = datetime.now()
    revenue_daily = db.query(models.Order).filter(
        models.Order.shop_id == shop_id, models.Order.created_at >= today).all()
    revenue_weekly = db.query(models.Order).filter(
        models.Order.shop_id == shop_id, models.Order.created_at >= today - timedelta(days=7)).all()
    revenue_monthly = db.query(models.Order).filter(
        models.Order.shop_id == shop_id, models.Order.created_at >= today - timedelta(days=30)).all()

    # return only numbers
    revenue_daily = sum([order.total for order in revenue_daily])
    revenue_weekly = sum([order.total for order in revenue_weekly])
    revenue_monthly = sum([order.total for order in revenue_monthly])

    return {"daily": revenue_daily, "weekly": revenue_weekly, "monthly": revenue_monthly}


def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    order.status = status
    db.commit()
    return order


def get_order_status(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    return order.status


def get_store_items(db: Session, shop_id: int):
    # return a dict where keys - categories, values - list of lists, [item_name, availability]
    items = db.query(models.Item).filter(models.Item.shop_id == shop_id).all()
    categories = set([item.category for item in items])
    items_by_categories = {}
    for category in categories:
        items_by_categories[category] = []

    for item in items:
        items_by_categories[item.category].append(
            [item.name, item.available, item.item_id])

    return items_by_categories


def toggle_item_availability(db: Session, item_id: int, availability: bool):
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not availability:
        item.available = not item.available
    else:
        item.available = availability
    db.commit()
    return item


def get_store_raw_materials(db: Session, shop_id: int):
    all_raw_materials = db.query(Base.metadata.tables['materials_stores']).filter(
        Base.metadata.tables['materials_stores'].c.store_id == shop_id).all()

    # return as list of [raw_material_name, available, raw_material_id]
    raw_materials = []
    for raw_material in all_raw_materials:
        raw_material_obj = db.query(models.RawMaterial).filter(
            models.RawMaterial.id == raw_material[1]).first()
        raw_materials.append(
            [raw_material_obj.name, raw_material[2], raw_material_obj.id])

    return raw_materials


def toggle_raw_material_availability(db: Session, raw_material_id: int, availability: bool, shop_id: int):
    # toggle in the intermediate table
    raw_material = db.query(Base.metadata.tables['materials_stores']).filter(Base.metadata.tables['materials_stores'].c.material_id ==
                                                                             raw_material_id, Base.metadata.tables['materials_stores'].c.store_id == shop_id).update({"available": availability})
    db.commit()
    return raw_material


def get_raw_material_stores(db: Session, raw_material_name: str, exclude: int):
    stores = db.query(models.RawMaterial).filter(
        models.RawMaterial.name == raw_material_name).first().stores
    print(stores)
    if exclude:
        stores = [store for store in stores if store.shop_id != exclude]
    return stores


def create_item(db: Session, shop_id: int, item: ItemCreate):
    new_item = models.Item(
        shop_id=shop_id,
        name=item.name,
        category=item.category,
        available=item.available,
        price=item.price,
        description=item.description
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item