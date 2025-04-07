from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/create")
def read_root():
    pass


@app.get("/verify/{ticket_id}")
def read_item(ticket_id: str):
    pass
