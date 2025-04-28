import io
import json
from datetime import datetime, timezone
from typing import Annotated

import jwt
import qrcode
from fastapi import Depends, FastAPI, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

import utils, config
import database

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
            content={"error": True, "message": f"Database connection error: {str(db_err)}"},
            media_type="application/json",
            status_code=500,
        )
    except database.DatabaseTimeoutError as timeout_err:
        return JSONResponse(
            content={"error": True, "message": f"Database timeout error: {str(timeout_err)}"},
            media_type="application/json",
            status_code=500,
        )
    except Exception as e:
        return JSONResponse(
            content={"error": True, "message": f"An unexpected error occurred: {str(e)}"},
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
        img = qrcode.make(jwt.encode(payload, config.JWT_MASTER_PASSWORD, algorithm="HS256"))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    
    except Exception as e:
        return JSONResponse(
            content={"error": True, "message": f"An unexpected error occured: {str(e)}"}
            media_type="application/json",
            status_code=500,
        )



# @app.get("/verify/{ticket_id}")
# def verify_ticket(
#     ticket_id: str,
#     credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
# ):

#     jwt_token = credentials.credentials
#     payload = jwt.decode(jwt_token, config.SECRET_KEY, algorithms=["HS256"])

#     data = cursor.child(ticket_id).get()

#     if data != payload:
#         return {
#             "error": True,
#             "message": "Invalid Ticket",
#             "code": "INVALID_TICKET",
#             "timestamp": datetime.now().isoformat(),
#         }

#     if data is None:
#         return {
#             "error": True,
#             "message": "Invalid Ticket",
#             "code": "INVALID_TICKET",
#             "timestamp": datetime.now().isoformat(),
#         }

#     if datetime.fromisoformat(data.get("valid_until")).astimezone(
#         timezone.utc
#     ) < datetime.now(timezone.utc):
#         return {
#             "error": True,
#             "message": "Ticket Expired",
#             "code": "TICKET_EXPIRED",
#             "timestamp": datetime.now().isoformat(),
#         }
#     else:
#         return {
#             "status": 200,
#             "message": "Verified",
#             "code": "TICKET_VALIDATED",
#             "timestamp": datetime.now().isoformat(),
#         }
