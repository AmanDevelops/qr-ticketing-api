from sqlalchemy import create_engine

from models import Base

# Example: PostgreSQL URI
DATABASE_URL = "postgresql://root:1234@localhost:5432/qr-ticketing"

engine = create_engine(DATABASE_URL)


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
