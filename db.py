from config import get_setting
import os
from typing import Union
import psycopg2

DB_NAME = get_setting('DB', 'db_name')
DB_USER = get_setting('DB', 'user')
DB_PASSWORD = get_setting('DB', 'password')
TABLE_NAME = get_setting('DB', 'db_table')
TABLE_SCHEMA = '''
record_id SERIAL PRIMARY KEY,
mac VARCHAR(17) NOT NULL,
temperature float NOT NULL,
humidity float NOT NULL,
pressure int NOT NULL,
voltage int NOT NULL,
tx_power int NOT null,
measurement_sequence int NOT NULL,
poll_start_ts timestamp with time zone
'''


class db_connector():
    def __init__(self):
        self.conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    def execute_query(self, query: str, values: tuple = None) -> None:
        with self.conn.cursor() as c:
            c.execute(query, values)
    
    def get_one(self, query: str) -> bool:
        with self.conn.cursor() as c:
            c.execute(query)
            return c.fetchone()

    def close(self):
        self.conn.close()


def init_db():
    db = db_connector()
    exists = db.get_one(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if not exists:
        db.execute_query(f'CREATE DATABASE {DB_NAME}')
    db.execute_query(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({TABLE_SCHEMA})')
    db.close()


def insert_record(record: dict):
    try:
        fixed_key_order = list(record.keys())
        values = tuple([record[key] for key in fixed_key_order])
        fields = ', '.join(fixed_key_order)
        query = f'INSERT INTO {TABLE_NAME} ({fields}) VALUES ({",".join(["%s"] * len(record))})'
        db = db_connector()
        db.execute_query(query, values)
        db.close()
    except BaseException as e:
        raise Exception(f'Error during record insert: {e}') from e


if __name__ == '__main__':
    init_db()
