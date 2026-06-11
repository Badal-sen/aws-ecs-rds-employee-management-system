from flask import Flask, request, redirect, render_template_string
import psycopg2
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Employee Dashboard</title>
</head>
<body>

<h1>Employee Management Dashboard</h1>
<p>AWS ECS + ECR + GitHub Actions CI/CD + PostgreSQL</p>

<h2>Total Employees: {{ count }}</h2>

<form method="POST" action="/add">
<input type="text" name="name" placeholder="Employee Name" required>
<input type="text" name="position" placeholder="Position" required>
<button type="submit">Add Employee</button>
</form>

<br>

<table border="1">
<tr>
<th>ID</th>
<th>Name</th>
<th>Position</th>
<th>Action</th>
</tr>

{% for employee in employees %}
<tr>
<td>{{ employee[0] }}</td>
<td>{{ employee[1] }}</td>
<td>{{ employee[2] }}</td>
<td>
<form method="POST" action="/delete/{{ employee[0] }}">
<button type="submit">Delete</button>
</form>
</td>
</tr>
{% endfor %}

</table>

</body>
</html>
"""

def get_db():
    print("Connecting to PostgreSQL...")

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5
    )

def init_db():
    try:
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

        print("Database initialized successfully")

    except Exception as e:
        print(f"DATABASE ERROR: {e}")

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

        return render_template_string(
            HTML,
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

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)