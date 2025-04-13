import os

import jwt
import requests


class VerifyPayments:
    def razorpay(payment_id: str):
        """
        For Reference: https://razorpay.com/docs/api/payments/fetch-with-id
        """

        uri = f"https://api.razorpay.com/v1/payments/{payment_id}"
        response = requests.get(
            uri,
            auth=(
                os.environ.get("RAZORPAY_KEY"),
                os.environ.get("RAZORPAY_KEY_SECRET"),
            ),
        )
        return True if response.get("status") == "captured" else False


class Encode:
    def jwt_encode(payload: dict, secret_key: str):
        return jwt.encode(payload, secret_key, algorithm="HS256")
