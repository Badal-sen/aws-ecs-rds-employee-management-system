from flask import Flask, request, redirect, render_template
import psycopg2
import os

app = Flask(__name__)

def get_db():
    print("Connecting to PostgreSQL...", flush=True)

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5
    )

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        position VARCHAR(100) NOT NULL
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def home():
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, position
            FROM employees
            ORDER BY id
        """)

        employees = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "index.html",
            employees=employees,
            count=len(employees)
        )

    except Exception as e:
        return f"Database Error: {e}", 500

@app.route("/add", methods=["POST"])
def add():
    try:
        name = request.form["name"]
        position = request.form["position"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO employees (name, position) VALUES (%s, %s)",
            (name, position)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    except Exception as e:
        return f"Database Error: {e}", 500

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM employees WHERE id = %s",
            (id,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    except Exception as e:
        return f"Database Error: {e}", 500

try:
    print("Starting application...", flush=True)
    init_db()
    print("Database initialization completed", flush=True)
except Exception as e:
    print(f"STARTUP DATABASE ERROR: {e}", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)