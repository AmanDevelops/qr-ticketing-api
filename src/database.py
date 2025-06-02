import psycopg2

connection = psycopg2.connect(
    host="db", dbname="qr-ticketing", user="root", password="1234", port=5432
)
