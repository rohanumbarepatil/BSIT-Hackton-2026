# database/db_connection.py

import psycopg2
import os


def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="wastesense_db",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )

    return conn