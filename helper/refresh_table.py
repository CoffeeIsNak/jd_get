import psycopg2
import os


# PostgreSQL 연결 정보
DB_HOST = 'postgres'
DB_PORT = 5432
DB_NAME = 'jd_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# PostgreSQL 연결 함수
def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_table(table_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE TABLE IF EXISTS jobs;
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title TEXT,
            company_name TEXT,
            url TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            UNIQUE (title, company_name. )
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
