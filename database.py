"""
AstraPay - Database initialisation script
Run once to create tables and seed demo data.
"""

import psycopg2
import os

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "astrapay"),
    "user": os.environ.get("DB_USER", "astrapay"),
    "password": os.environ.get("DB_PASS", "astrapay123"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
}


def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            bio TEXT DEFAULT '',
            balance NUMERIC(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            recipient VARCHAR(100),
            amount NUMERIC(10, 2),
            note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        INSERT INTO users (username, password, email, balance) VALUES
            ('admin',    'admin123',    'admin@astrapay.com',   99999.00),
            ('john.doe', 'password',    'john@astrapay.com',    4250.75),
            ('jane.doe', 'jane2024',    'jane@astrapay.com',    1800.50),
            ('bob.smith','qwerty123',   'bob@astrapay.com',     320.00)
        ON CONFLICT (username) DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO transactions (user_id, recipient, amount, note) VALUES
            (2, 'jane.doe',  250.00, 'Rent split'),
            (2, 'bob.smith',  50.00, 'Lunch'),
            (3, 'john.doe',  100.00, 'Concert tickets'),
            (4, 'jane.doe',   75.25, 'Groceries')
        ON CONFLICT DO NOTHING;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialised successfully.")


if __name__ == "__main__":
    init_db()
