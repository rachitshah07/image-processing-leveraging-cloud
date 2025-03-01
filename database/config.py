import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2
from psycopg2 import OperationalError, Error
from dotenv import load_dotenv
import urllib.parse
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy

if os.environ.get("ENV","deployment")=="local":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(BASE_DIR):
        load_dotenv(BASE_DIR)


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "image_processing")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
LOCAL_ENV = os.getenv("ENV","deployment")
encoded_password = urllib.parse.quote_plus(DB_PASS)

Base = declarative_base()
SessionLocal = None
engine = None


def create_database_if_not_exists():
    """Creates local database if not exists"""
    try:
        connection = psycopg2.connect(
            dbname=DB_USER, user=DB_USER, password=DB_PASS, host=DB_HOST
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
    except (OperationalError, Error) as e:
        print(f"Database connection error: {e}")


def connect_with_connector():
    """Connect to Cloud SQL with Google Cloud SQL Connector"""
    ip_type =IPTypes.PUBLIC
    connector = Connector(refresh_strategy="LAZY")

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_string=INSTANCE_CONNECTION_NAME,
            driver="pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=ip_type,
        )
        return conn

    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)


if LOCAL_ENV == "local":
    print("Running in Local Environment")
    DB_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
    create_database_if_not_exists()
    try:
        engine = create_engine(DB_URL)
        print("Local SQLAlchemy Engine created successfully.")
    except Exception as e:
        print(f"Failed to create Local Engine: {e}")

else:
    print("Running in Cloud Environment")
    try:
        engine = connect_with_connector()
        print("Cloud SQL Engine created successfully.")
    except Exception as e:
        print(f"Failed to create Cloud SQL Engine: {e}")

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)