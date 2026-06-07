from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

employees = [
    {"id": 1, "name": "John Smith", "position": "Developer"},
    {"id": 2, "name": "Sarah Johnson", "position": "Manager"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Management System</title>
</head>
<body>
    <h1>Employee Management System</h1>

    <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Employee Name" required>
        <input type="text" name="position" placeholder="Position" required>
        <button type="submit">Add Employee</button>
    </form>

    <hr>

    <ul>
    {% for employee in employees %}
        <li>
            {{ employee.name }} - {{ employee.position }}

            <form method="POST"
                  action="/delete/{{ employee.id }}"
                  style="display:inline;">
                <button type="submit">Delete</button>
            </form>
        </li>
    {% endfor %}
    </ul>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, employees=employees)

@app.route("/add", methods=["POST"])
def add():
    employees.append({
        "id": len(employees) + 1,
        "name": request.form["name"],
        "position": request.form["position"]
    })
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    global employees
    employees = [e for e in employees if e["id"] != id]
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)