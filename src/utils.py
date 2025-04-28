import datetime
import json

import jwt

import config
from database import connection


def create_event(
    name: str, event_time: datetime.datetime, location: str, ticket_capacity: int
) -> int:
    query = """
        INSERT INTO events.events (name, event_time, location, ticket_capacity)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    values = (name, event_time, location, ticket_capacity)

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        result = cursor.fetchone()
        last_inserted_id = None

        if result:
            last_inserted_id = result[0]

        connection.commit()
        return last_inserted_id


def create_ticket(user_id: int, event_id: int, metadata: dict = None) -> int:
    last_inserted_id = None
    query = """
        INSERT INTO events.tickets (user_id, event_id, metadata)
        VALUES (%s, %s, %s::jsonb)
        RETURNING id;
    """

    values = (user_id, event_id, json.dumps(metadata) if metadata else None)

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        result = cursor.fetchone()
        last_inserted_id = None

        if result:
            last_inserted_id = result[0]

        connection.commit()
        return last_inserted_id


def create_user(first_name: str, username: str) -> int:
    query = """
        INSERT INTO authentication.users (first_name, username)
        VALUES (%s, %s)
        RETURNING id;
    """

    values = (first_name, username)

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        result = cursor.fetchone()

        if result:
            last_inserted_id = result[0]

        connection.commit()
        return last_inserted_id


def fetch_ticket_details(ticket_id: int) -> tuple:
    query = """
        SELECT 
            u.first_name AS first_name, 
            u.is_active AS is_active,
            e.name AS event_name,
            e.event_time AS event_time,
            t.ticket_status AS ticket_status
        FROM authentication.users u
        JOIN events.tickets t ON t.user_id = u.id
        JOIN events.events e ON t.event_id = e.id
        WHERE t.id = %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (ticket_id,))
        return cursor.fetchone()
