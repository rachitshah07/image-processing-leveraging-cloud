import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2
from psycopg2 import OperationalError, Error
from dotenv import load_dotenv
import urllib.parse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(BASE_DIR)


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "image_processing")
encoded_password = urllib.parse.quote_plus(DB_PASS)

DB_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
def create_database_if_not_exists():
    try:
        connection = psycopg2.connect(
            dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST
        )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cursor.close()
        connection.close()
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except Error as e:
        print(f"Database error: {e}")

create_database_if_not_exists()

try:
    engine = create_engine(DB_URL)
    print(" SQLAlchemy Engine created successfully.")
except Exception as e:
    print(f"Failed to create SQLAlchemy Engine: {e}")

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


Base = declarative_base()
