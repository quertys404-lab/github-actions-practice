
from flask import Flask, jsonify
import psycopg2
import os
import time

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "myapp"),
        user=os.getenv("DB_USER", "app_user"),
        password=os.getenv("DB_PASSWORD", "secure_password")
    )

def init_db():
    for attempt in range(30):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                )
            """)
            cur.execute("""
                INSERT INTO items (name)
                SELECT 'Test item'
                WHERE NOT EXISTS (SELECT 1 FROM items)
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized")
            return
        except Exception as error:
            print(f"Waiting for database: {error}")
            time.sleep(2)

    raise RuntimeError("Database connection failed")

@app.route("/")
def home():
    return """
    <h1>GitHub Actions Practice</h1>
    <p>Application is running!</p>
    <p><a href='/api/items'>View items</a></p>
    """

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as error:
        return jsonify({"status": "unhealthy", "error": str(error)}), 500

@app.route("/api/data")
def api_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM items")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({"database_connected": True, "count": count})

@app.route("/api/items")
def api_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": row[0], "name": row[1]} for row in rows])

@app.route("/api/items/count")
def items_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM items")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return str(count)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=3000)
