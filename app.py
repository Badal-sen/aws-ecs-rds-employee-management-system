from flask import Flask, request, redirect, render_template, session
import sqlite3
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

DATABASE = "employees.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        print("Database schema initialized")
    except Exception as e:
        conn.rollback()
        print(f"ERROR during init_db: {e}")
        raise
    finally:
        conn.close()

def validate_input(name, position):
    errors = []
    
    if not name or not name.strip():
        errors.append("Name is required")
    elif len(name) > 100:
        errors.append("Name must be 100 characters or less")
    
    if not position or not position.strip():
        errors.append("Position is required")
    elif len(position) > 100:
        errors.append("Position must be 100 characters or less")
    
    return errors

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def verify_csrf_token(token):
    return token == session.get('_csrf_token')

@app.before_request
def before_request():
    app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.route("/")
def home():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, position FROM employees ORDER BY id")
        employees = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"ERROR fetching employees: {e}")
        employees = []
    finally:
        conn.close()
    
    return render_template("index.html", employees=employees, count=len(employees))

@app.route("/add", methods=["POST"])
def add():
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    
    errors = validate_input(name, position)
    if errors:
        return render_template("index.html", employees=[], error=", ".join(errors)), 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position) VALUES (?, ?)",
            (name, position)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"ERROR inserting employee: {e}")
        return "Failed to add employee", 500
    finally:
        conn.close()
    
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, position FROM employees WHERE id = ?", (id,))
        employee = cursor.fetchone()
        cursor.close()
    except Exception as e:
        print(f"ERROR fetching employee: {e}")
        employee = None
    finally:
        conn.close()
    
    if not employee:
        return "Employee not found", 404
    
    return render_template("edit.html", employee=employee)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    
    errors = validate_input(name, position)
    if errors:
        return render_template("edit.html", employee=(id, name, position), error=", ".join(errors)), 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employees SET name = ?, position = ? WHERE id = ?",
            (name, position, id)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"ERROR updating employee: {e}")
        return "Failed to update employee", 500
    finally:
        conn.close()
    
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"ERROR deleting employee: {e}")
        return "Failed to delete employee", 500
    finally:
        conn.close()
    
    return redirect("/")

@app.errorhandler(500)
def handle_500(e):
    return "Internal server error", 500

@app.errorhandler(404)
def handle_404(e):
    return "Page not found", 404

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        exit(1)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
