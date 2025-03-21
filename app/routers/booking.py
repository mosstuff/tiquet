from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app import crud, schemas, utillities
from app.config import reload_settings, update_settings
from app.dependencies import get_db
from datetime import datetime, timedelta
router = APIRouter()
global settings
settings = reload_settings()
global terminalState
terminalState = {}

@router.post("/booking/create_booking", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db=db, qr_code=booking.qr_code)
    if db_booking is None:
        return crud.create_booking(db=db, booking=booking)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="QR-Code already in database")

@router.get("/booking/get_booking/{qr_code}", response_model=schemas.Booking)
def read_booking(qr_code: str, db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db=db, qr_code=qr_code)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return db_booking

@router.get("/booking/get_booking", response_model=list[schemas.BookingResponse])
def read_bookings(db: Session = Depends(get_db)):
    db_booking = crud.get_bookings(db=db)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Bookings in Database")
    return db_booking

@router.get("/booking/delete_booking/{qr_code}")
def delete_booking(qr_code: str, db: Session = Depends(get_db)):
    success = crud.remove_booking(db=db, qr_code=qr_code)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"detail": "Booking deleted successfully"}

@router.post("/booking/checkin/{qr_code}")
def checkin(qr_code: str, db: Session = Depends(get_db)):
    db_entry = crud.get_booking(db=db, qr_code=qr_code)
    if not db_entry:
        return {
            "status": "Booking not found!",
        }

    activity = getattr(db_entry, "activity", None)
    try:
        activity = settings.activities[activity]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activity not found")
    offset = activity["offset"]

    current_range = utillities.get_current_time_range_str(offset)
    next_range = utillities.get_next_time_range_str(offset)

    booked_slot = getattr(db_entry, "timeslot", None)
    if getattr(db_entry, "arrived", None) == True:
        return {
            "status": "duplicate"
        }
    elif booked_slot == current_range or booked_slot == next_range:
        crud.update_booking_status(db=db, qr_code=qr_code, new_status=True)
        return {
            "status": "success",
            "name": getattr(db_entry, "name", None),
            "activity": getattr(db_entry, "activity", None)
        }
    elif booked_slot < current_range:
        return {
            "status": "Missed!"
        }
    elif booked_slot > current_range:
        return {
            "status": "Too early!"
        }

@router.get("/config")
def get_config():

    system_time = datetime.now(utillities.get_timezone()).strftime('%H:%M')

    return {
        "app_name": settings.app_name,
        "setup_complete": settings.setup_complete,
        #"all_timeslots": timeslots,
        "activities": settings.activities,
        "system_time": system_time
    }

@router.get("/config/get_timeframe_by_activity")
def get_timeframe_by_activity(activity: str):
    try:
        activity = settings.activities[activity]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activity not found")
    offset = activity["offset"]
    timeslots = utillities.get_all_timeslots(offset)
    return timeslots

@router.get("/config/get_timeframe_by_offset")
def get_timeframe_by_offset(offset: int):
    timeslots = utillities.get_all_timeslots(offset)
    return timeslots

@router.get("/config/reload")
def reloadConfig():
    global settings
    settings = reload_settings()
    return {"detail": "Settings reloaded successfully"}

@router.post("/config/update-config", status_code=200)
def update_setting(config: schemas.ConfigUpdate, response: Response):
    global settings
    data = config.model_dump()
    try:
        settings = update_settings(data.get("key"), data.get("value"))
        return {"detail": "Setting updated successfully"}
    except:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@router.get("/state/booking/{terminal}")
def getTerminalBookingState(terminal: str):
    state = terminalState[terminal]
    return state

@router.get("/state/booking/{terminal}/set/{state}")
def getTerminalBookingState(terminal: str, state: str):
    terminalState[terminal] = state
    state = terminalState[terminal]
    return state