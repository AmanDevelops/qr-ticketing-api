import jwt
import datetime
from database import connection

def jwt_encode(payload: dict, secret_key: str):
    return jwt.encode(payload, secret_key, algorithm="HS256")


def create_ticket(name: str, event_time: datetime.datetime, location: str, ticket_capacity: int) -> None:
    query = """
        INSERT INTO events.events (name, event_time, location, ticket_capacity)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    values = (name, event_time, location, ticket_capacity)

    with connection.cursor() as cursor:
        cursor.execute(query, values)

        result = cursor.fetchone()

        if result:
            last_inserted_id = result[0]

        connection.commit()

        return last_inserted_id