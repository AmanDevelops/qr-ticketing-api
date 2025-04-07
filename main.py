import io
import os
import time
from typing import Union

import jwt
import qrcode
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database import cursor

app = FastAPI()

load_dotenv()


class UserDetails(BaseModel):
    ticketId: int
    name: str | None = None
    seatInfo: str | None = None
    price: float | None = None
    paymentId: str
    # Add Others as you wish


@app.post("/create", response_class=Response)
def create_qr(user: UserDetails):
    # Check if Payment is verified or Not

    if True:  # Condition to check payment
        payload = {
            "ticketId": user.ticketId,
            "name": user.name,
            "seatInfo": user.seatInfo,
            "price": user.price,
            "paymentId": user.paymentId,
            "timestamp": int(time.time()),
        }
        img = qrcode.make(
            jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
        )

        cursor.set(
            {
                user.ticketId: {
                    "name": user.name,
                    "seatInfo": user.seatInfo,
                    "price": user.price,
                    "paymentId": user.paymentId,
                    "timestamp": int(time.time()),
                }
            }
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")


@app.get("/verify/{ticket_id}")
def read_item(ticket_id: str):
    pass
