import io
from datetime import datetime, timezone

import jwt
import qrcode
from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel

import config
import database
import utils

app = FastAPI()
security = HTTPBearer()


class TicketDetails(BaseModel):
    user_id: int
    event_id: int
    metadata: dict


class EventDetails(BaseModel):
    name: str
    event_time: datetime
    location: str
    ticket_capacity: int


@app.post("/events/create", response_class=Response)
def create_event(event_detail: EventDetails):
    """
    Args:
        event_detail (EventDetails): The details of the event to be created, including name, event time, location, and ticket capacity.

    Returns:
        dict: A response indicating success or failure of the event creation.
    """
    try:
        event_id = utils.create_event(
            name=event_detail.name,
            event_time=event_detail.event_time,
            location=event_detail.location,
            ticket_capacity=event_detail.ticket_capacity,
        )
        return JSONResponse(
            content={"success": True, "event_id": event_id},
            media_type="application/json",
            status_code=200,
        )
    except database.DatabaseConnectionError as db_err:
        return JSONResponse(
            content={
                "error": True,
                "message": f"Database connection error: {str(db_err)}",
            },
            media_type="application/json",
            status_code=500,
        )
    except database.DatabaseTimeoutError as timeout_err:
        return JSONResponse(
            content={
                "error": True,
                "message": f"Database timeout error: {str(timeout_err)}",
            },
            media_type="application/json",
            status_code=500,
        )
    except Exception as e:
        return JSONResponse(
            content={
                "error": True,
                "message": f"An unexpected error occurred: {str(e)}",
            },
            media_type="application/json",
            status_code=500,
        )


@app.post("/tickets/create", response_class=Response)
def create_qr(user: TicketDetails):

    try:
        ticket_id = utils.create_ticket(user.user_id, user.event_id, user.metadata)
        payload = {
            "user_id": user.user_id,
            "event_id": user.event_id,
            "ticket_id": ticket_id,
            "metadata": user.metadata,
        }
        img = qrcode.make(
            jwt.encode(payload, config.JWT_MASTER_PASSWORD, algorithm="HS256")
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png", status_code=200)

    except Exception as e:
        return JSONResponse(
            content={
                "error": True,
                "message": f"An unexpected error occured: {str(e)}",
            },
            media_type="application/json",
            status_code=500,
        )


@app.get("/verify/{ticket_id}")
def verify_ticket(ticket_id: str):
    data = utils.fetch_ticket_details(ticket_id=ticket_id)

    if data is None:
        return {
            "error": True,
            "message": "Invalid Ticket",
            "code": "INVALID_TICKET",
            "timestamp": datetime.now().isoformat(),
        }

    if data[3] < datetime.now(timezone.utc):
        return {
            "error": True,
            "message": "Ticket Expired",
            "code": "TICKET_EXPIRED",
            "timestamp": datetime.now().isoformat(),
        }

    if not data[1]:
        return {
            "error": True,
            "message": "User Disabled",
            "code": "USER_DISABLED",
            "timestamp": datetime.now().isoformat(),
        }
    if data[4] == 1:
        return {
            "status": 200,
            "message": "Verified",
            "code": "TICKET_VALIDATED",
            "metadata": {
                "ticket_id": ticket_id,
                "first_name": data[0],
                "isActive": data[1],
                "event_name": data[2],
                "event_time": data[3],
            },
            "timestamp": datetime.now().isoformat(),
        }
