import io
from datetime import datetime

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

    isPaid = (
        utils.VerifyPayments.razorpay(user.payment_id)
        if config.PAYMENT_VERIFICATION
        else True
    )

    if isPaid:
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
    pass
