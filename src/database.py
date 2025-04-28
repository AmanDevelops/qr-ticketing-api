import psycopg2

connection = psycopg2.connect(
    host="localhost", dbname="qr-ticketing", user="postgres", password="root", port=5432
)
