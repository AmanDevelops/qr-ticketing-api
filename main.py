import io
from datetime import datetime, timezone

import qrcode
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
import utils
from database import cursor

app = FastAPI()


class UserDetails(BaseModel):
    event_id: int
    ticket_id: int
    payment_id: str
    valid_until: datetime
    metadata: dict | None = None


@app.post("/create", response_class=Response)
def create_qr(user: UserDetails):

    is_paid = (
        utils.VerifyPayments.razorpay(user.payment_id)
        if config.PAYMENT_VERIFICATION
        else True
    )

    if is_paid:
        payload = {
            "event_id": user.event_id,
            "ticket_id": user.ticket_id,
            "payment_id": user.payment_id,
            "valid_until": user.valid_until.isoformat(),
            "metadata": user.metadata,
        }

        img = qrcode.make(utils.Encode.jwt_encode(payload, config.SECRET_KEY))

        cursor.child(str(user.ticket_id)).set(payload)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")


@app.get("/verify/{ticket_id}")
def verify_ticket(ticket_id: str):
    data = cursor.child(ticket_id).get()

    if data is None:
        return {
            "error": True,
            "message": "Invalid Ticket",
            "code": "INVALID_TICKET",
            "timestamp": datetime.now().isoformat(),
        }

    if datetime.fromisoformat(data.get("valid_until")).astimezone(
        timezone.utc
    ) < datetime.now(timezone.utc):
        return {
            "error": True,
            "message": "Ticket Expired",
            "code": "TICKET_EXPIRED",
            "timestamp": datetime.now().isoformat(),
        }
    else:
        return {
            "status": 200,
            "message": "Verified",
            "code": "TICKET_VALIDATED",
            "timestamp": datetime.now().isoformat(),
        }
