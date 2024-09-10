from pydantic import BaseModel

class BookingBase(BaseModel):
    name: str
    ph_desc: str
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
        orm_mode = True

class BookingResponse(BaseModel):
    id: int
    name: str
    ph_desc: str
    activity: str
    timeslot: str
    qr_code: str
    arrived: bool
    subactivity: str

    class Config:
        orm_mode = True

class ConfigUpdate(BaseModel):
    key: str
    value: str