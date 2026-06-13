from flask import Flask, request, redirect, render_template, session
import psycopg2
from psycopg2 import pool
import os
import secrets
import sys

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

db_pool = None

def init_pool():
    """Initialize PostgreSQL connection pool"""
    global db_pool
    try:
        db_host = os.environ.get("DB_HOST", "localhost")
        db_name = os.environ.get("DB_NAME", "employees_db")
        db_user = os.environ.get("DB_USER", "postgres")
        db_password = os.environ.get("DB_PASSWORD", "")
        
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        print("[APP] Database pool initialized successfully")
        return True
    except Exception as e:
        print(f"[APP] FATAL: Failed to create database pool: {e}", file=sys.stderr)
        return False

def get_db():
    """Get connection from pool"""
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    try:
        return db_pool.getconn()
    except Exception as e:
        print(f"[APP] ERROR: Failed to get database connection: {e}", file=sys.stderr)
        raise

def return_db(conn):
    """Return connection to pool"""
    if db_pool and conn:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            print(f"[APP] WARNING: Failed to return connection to pool: {e}", file=sys.stderr)

def init_db():
    """Initialize database schema"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                position VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        print("[APP] Database schema initialized")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[APP] FATAL: Database initialization failed: {e}", file=sys.stderr)
        return False
    finally:
        if conn:
            return_db(conn)

def validate_input(name, position):
    """Validate employee input"""
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
    """Generate CSRF token"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def verify_csrf_token(token):
    """Verify CSRF token"""
    return token == session.get('_csrf_token')

@app.before_request
def before_request():
    """Make CSRF token available to templates"""
    app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.route("/")
def home():
    """List all employees"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, position FROM employees ORDER BY id")
        employees = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"[APP] ERROR in home(): {e}", file=sys.stderr)
        employees = []
    finally:
        if conn:
            return_db(conn)
    
    return render_template("index.html", employees=employees, count=len(employees))

@app.route("/add", methods=["POST"])
def add():
    """Add new employee"""
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    
    errors = validate_input(name, position)
    if errors:
        conn = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, position FROM employees ORDER BY id")
            employees = cursor.fetchall()
            cursor.close()
        except:
            employees = []
        finally:
            if conn:
                return_db(conn)
        
        return render_template("index.html", employees=employees, error=", ".join(errors)), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position) VALUES (%s, %s)",
            (name, position)
        )
        conn.commit()
        cursor.close()
        print(f"[APP] Employee added: {name}")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[APP] ERROR in add(): {e}", file=sys.stderr)
        return "Failed to add employee", 500
    finally:
        if conn:
            return_db(conn)
    
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    """Edit employee page"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, position FROM employees WHERE id = %s", (id,))
        employee = cursor.fetchone()
        cursor.close()
    except Exception as e:
        print(f"[APP] ERROR in edit(): {e}", file=sys.stderr)
        employee = None
    finally:
        if conn:
            return_db(conn)
    
    if not employee:
        return "Employee not found", 404
    
    return render_template("edit.html", employee=employee)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    """Update employee"""
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    
    errors = validate_input(name, position)
    if errors:
        return render_template("edit.html", employee=(id, name, position), error=", ".join(errors)), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employees SET name = %s, position = %s WHERE id = %s",
            (name, position, id)
        )
        conn.commit()
        cursor.close()
        print(f"[APP] Employee updated: ID {id}")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[APP] ERROR in update(): {e}", file=sys.stderr)
        return "Failed to update employee", 500
    finally:
        if conn:
            return_db(conn)
    
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Delete employee"""
    if not verify_csrf_token(request.form.get("csrf_token")):
        return "CSRF token validation failed", 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        print(f"[APP] Employee deleted: ID {id}")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[APP] ERROR in delete(): {e}", file=sys.stderr)
        return "Failed to delete employee", 500
    finally:
        if conn:
            return_db(conn)
    
    return redirect("/")

@app.errorhandler(500)
def handle_500(e):
    print(f"[APP] 500 Error: {e}", file=sys.stderr)
    return "Internal server error", 500

@app.errorhandler(404)
def handle_404(e):
    return "Page not found", 404

@app.route("/health")
def health():
    """Health check endpoint for ALB"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return_db(conn)
        return {"status": "healthy"}, 200
    except Exception as e:
        print(f"[APP] Health check failed: {e}", file=sys.stderr)
        return {"status": "unhealthy"}, 503

# Initialize database when running under Gunicorn
if db_pool is None:
    print("[APP] Initializing database for Gunicorn...")
    if init_pool():
        init_db()
    

if __name__ == "__main__":
    print("[APP] Starting Flask application...")
    
    if not init_pool():
        print("[APP] FATAL: Could not initialize database pool")
        exit(1)
    
    if not init_db():
        print("[APP] FATAL: Could not initialize database schema")
        exit(1)
    
    print("[APP] Application ready")
    app.run(host="0.0.0.0", port=5000, debug=False)
