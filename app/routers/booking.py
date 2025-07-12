from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app import crud, schemas, utillities
from app.config import reload_settings, update_settings
from app.dependencies import get_db
from datetime import datetime
router = APIRouter()
global settings
settings = reload_settings()

global terminalState
terminalState = {}

@router.post("/booking/create_booking", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    db_booking = crud.get_booking_by_qr(db=db, qr_code=booking.qr_code)
    if db_booking is None:
        return crud.create_booking(db=db, booking=booking)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="QR-Code already in database")

@router.get("/booking/get_booking/{qr_code}", response_model=schemas.Booking)
def read_booking(qr_code: str, db: Session = Depends(get_db)):
    db_booking = crud.get_booking_by_qr(db=db, qr_code=qr_code)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return db_booking

@router.get("/booking/get_booking", response_model=list[schemas.BookingResponse])
def read_bookings(db: Session = Depends(get_db)):
    db_booking = crud.get_bookings(db=db)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Bookings in Database")
    return db_booking

@router.post("/booking/delete_booking/{qr_code}")
def delete_booking(qr_code: str, db: Session = Depends(get_db)):
    success = crud.remove_booking(db=db, qr_code=qr_code)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"detail": "Booking deleted successfully"}

@router.post("/booking/checkin/{qr_code}")
def checkin(qr_code: str, db: Session = Depends(get_db)):
    db_entry = crud.get_booking_by_qr(db=db, qr_code=qr_code)
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
        "activities": settings.activities,
        "system_time": system_time
    }

@router.get("/config/planes")
def get_planes():
    return settings.planes

@router.get("/config/airports")
def get_airports():
    return settings.airports

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

@router.get("/routemanagement/get")
def get_current_and_next_routeinfo_by_activity(activity: str, db: Session = Depends(get_db)):

    try:
        activitydir = settings.activities[activity]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activity not found")
    offset = activitydir["offset"]

    current_slot = utillities.get_current_time_range_str(offset)
    next_slot = utillities.get_next_time_range_str(offset)

    db_entry = crud.get_bookings_by_activity(db=db, activity=activity)

    if not db_entry:
        return {
            "status": "No entries!",
        }

    entry_current = next((entry for entry in db_entry if entry.timeslot == current_slot), None)
    entry_next = next((entry for entry in db_entry if entry.timeslot == next_slot), None)

    if entry_current:
        id_current = entry_current.subactivity
        name_current = entry_current.name
    else:
        id_current = "0000"
        name_current = "n/a"
    if entry_next:
        id_next = entry_next.subactivity
        name_next = entry_next.name
    else:
        id_next = "0000"
        name_next = "n/a"

    current_ap, current_pl = int(id_current[:2]), int(id_current[2:])
    next_ap, next_pl = int(id_next[:2]), int(id_next[2:])

    return {
        "current": {
            "airport": current_ap,
            "plane": current_pl,
            "name": name_current
        },
        "next": {
            "airport": next_ap,
            "plane": next_pl,
            "name": name_next
        }
    }

@router.get("/routemanagement/getstr")
def get_current_and_next_routeinfo_by_activity_str(activity: str, db: Session = Depends(get_db)):
    try:
        activitydir = settings.activities[activity]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="activity not found")
    offset = activitydir["offset"]

    current_slot = utillities.get_current_time_range_str(offset)
    next_slot = utillities.get_next_time_range_str(offset)

    db_entry = crud.get_bookings_by_activity(db=db, activity=activity)

    if not db_entry:
        return {
            "status": "No entries!",
        }

    entry_current = next((entry for entry in db_entry if entry.timeslot == current_slot), None)
    entry_next = next((entry for entry in db_entry if entry.timeslot == next_slot), None)

    if entry_current:
        id_current = entry_current.subactivity
        name_current = entry_current.name
    else:
        id_current = "0000"
        name_current = "N/A"
    if entry_next:
        id_next = entry_next.subactivity
        name_next = entry_next.name
    else:
        id_next = "0000"
        name_next = "N/A"

    current_ap, current_pl = id_current[:2], id_current[2:]
    current_ap_str = settings.airports.get(current_ap, {}).get("name", "N/A")
    current_pl_str = settings.planes.get(current_pl, {}).get("name", "N/A")
    next_ap, next_pl = id_next[:2], id_next[2:]
    next_ap_str = settings.airports.get(next_ap, {}).get("name", "N/A")
    next_pl_str = settings.planes.get(next_pl, {}).get("name", "N/A")

    return {
        "current": {
            "airport": current_ap_str,
            "plane": current_pl_str,
            "name": name_current
        },
        "next": {
            "airport": next_ap_str,
            "plane": next_pl_str,
            "name": name_next
        }
    }