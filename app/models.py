from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ph_desc = Column(String)
    activity = Column(String)
    timeslot = Column(String)
    qr_code = Column(String)
    arrived = Column(Boolean, default=False)
    subactivity = Column(String)

    def __str__(self):
        return (f"Booking(id={self.id}, name={self.name}, ph_desc={self.ph_desc}, "
                f"activity={self.activity}, timeslot={self.timeslot}, qr_code={self.qr_code}, "
                f"arrived={self.arrived}, subactivity={self.subactivity})")

    def __repr__(self):
        return self.__str__()