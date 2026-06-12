from flask import Flask, request, redirect, render_template
import psycopg2
import os

app = Flask(**name**)

def get_db():
return psycopg2.connect(
host=os.environ["DB_HOST"],
database=os.environ["DB_NAME"],
user=os.environ["DB_USER"],
password=os.environ["DB_PASSWORD"]
)

def init_db():
conn = get_db()
cursor = conn.cursor()

```
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
```

@app.route("/")
def home():
conn = get_db()
cursor = conn.cursor()

```
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
```

@app.route("/add", methods=["POST"])
def add():
name = request.form["name"]
position = request.form["position"]

```
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
```

@app.route("/edit/[int:id](int:id)")
def edit(id):
conn = get_db()
cursor = conn.cursor()

```
cursor.execute(
    "SELECT id, name, position FROM employees WHERE id = %s",
    (id,)
)

employee = cursor.fetchone()

cursor.close()
conn.close()

return render_template(
    "edit.html",
    employee=employee
)
```

@app.route("/update/[int:id](int:id)", methods=["POST"])
def update(id):
name = request.form["name"]
position = request.form["position"]

```
conn = get_db()
cursor = conn.cursor()

cursor.execute(
    """
    UPDATE employees
    SET name = %s,
        position = %s
    WHERE id = %s
    """,
    (name, position, id)
)

conn.commit()
cursor.close()
conn.close()

return redirect("/")
```

@app.route("/delete/[int:id](int:id)", methods=["POST"])
def delete(id):
conn = get_db()
cursor = conn.cursor()

```
cursor.execute(
    "DELETE FROM employees WHERE id = %s",
    (id,)
)

conn.commit()
cursor.close()
conn.close()

return redirect("/")
```

try:
init_db()
except Exception as e:
print(f"STARTUP DATABASE ERROR: {e}")

if **name** == "**main**":
app.run(host="0.0.0.0", port=5000)
