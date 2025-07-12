from pydantic import BaseModel

class BookingBase(BaseModel):
    name: str
    activity: str
    timeslot: str
    qr_code: str
    arrived: bool
    subactivity: str

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int

    class Config:
        from_attributes = True

class BookingResponse(BaseModel):
    id: int
    name: str
    activity: str
    timeslot: str
    qr_code: str
    arrived: bool
    subactivity: str

    class Config:
        from_attributes = True

class ConfigUpdate(BaseModel):
    key: str
    value: str