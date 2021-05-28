from config import get_setting
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
TAG_TABLE_NAME = get_setting('DB', 'tag_name_table')
TAG_TABLE_SCHEMA = '''
mac VARCHAR(17) PRIMARY KEY,
tag_name VARCHAR(100) NOT NULL
'''


class DBConn:
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

    def close(self) -> None:
        self.conn.close()


def fill_tag_table(db: DBConn) -> None:
    tag_macs = [s.lower() for s in get_setting('TAG_FILTER', 'mac_addresses').split(',')]
    tag_names = [s.lower() for s in get_setting('TAG_FILTER', 'tag_names').split(',')]
    if len(tag_macs) != len(tag_names):
        raise Exception('Different amt of tag names and addresses')
    for mac, name in zip(tag_macs, tag_names):
        db.execute_query(f"INSERT INTO {TAG_TABLE_NAME} (mac, tag_name) VALUES ('{mac}', '{name}')")


def init_db() -> None:
    db = DBConn()
    exists = db.get_one(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if not exists:
        db.execute_query(f'CREATE DATABASE {DB_NAME}')
    db.execute_query(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({TABLE_SCHEMA})')
    db.execute_query(f'CREATE TABLE IF NOT EXISTS {TAG_TABLE_NAME} ({TAG_TABLE_SCHEMA})')
    fill_tag_table(db)
    db.close()


def insert_record(record: dict) -> None:
    try:
        fixed_key_order = list(record.keys())
        values = tuple([record[key] for key in fixed_key_order])
        fields = ', '.join(fixed_key_order)
        query = f'INSERT INTO {TABLE_NAME} ({fields}) VALUES ({",".join(["%s"] * len(record))})'
        db = DBConn()
        db.execute_query(query, values)
        db.close()
    except BaseException as e:
        raise Exception(f'Error during record insert: {e}') from e


if __name__ == '__main__':
    init_db()
