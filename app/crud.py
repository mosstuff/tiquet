from sqlalchemy.orm import Session
from . import models, schemas

def get_booking(db: Session, qr_code: str):
    return db.query(models.Booking).filter(models.Booking.qr_code == qr_code).first()

def get_bookings(db: Session):
    return db.query(models.Booking).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def remove_booking(db: Session, qr_code: str):
    db.query(models.Booking).filter(models.Booking.qr_code == qr_code).delete()
    db.commit()
    return True

def update_booking_status(db: Session, qr_code: str, new_status: bool):
    booking = db.query(models.Booking).filter(models.Booking.qr_code == qr_code).first()
    if booking:
        booking.arrived = new_status
        db.commit()
        db.refresh(booking)
        return booking
    return None
