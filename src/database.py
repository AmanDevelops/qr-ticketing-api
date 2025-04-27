import psycopg2

connection = psycopg2.connect(host="localhost", dbname="qr-ticketing", user="postgres", password="root", port=5432)
cursor = connection.cursor()

def read_query(query: str) -> psycopg2.extensions.cursor:
    """
    Args:
        query(str): processes query to the database
    """
    cursor.execute(query)
    return cursor


def write_query(query: str) -> psycopg2.extensions.cursor:
    """
    Args:
        query(str): writes query to the database
    """
    cursor.execute(query)
    connection.commit()
    return cursor