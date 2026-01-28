from flask import Flask, render_template, request, redirect, session, url_for, send_file
from models import init_db, get_db
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------- HOME ----------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    search = request.args.get("search", "")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM materials WHERE name LIKE ?", (f"%{search}%",))
    materials = cur.fetchall()
    conn.close()
    return render_template("index.html", materials=materials)

# ---------- CATEGORY PAGE ----------
@app.route("/category/<cat>")
def category(cat):
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM materials WHERE category=?", (cat,))
    materials = cur.fetchall()
    conn.close()
    return render_template("category.html", materials=materials, category=cat)

# ---------- UPLOAD ----------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    df = pd.read_excel(path)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ["name", "category", "force", "stress", "strain", "elasticity"]:
        if col not in df.columns:
            df[col] = None
    conn = get_db()
    cur = conn.cursor()
    for _, r in df.iterrows():
        cur.execute("""
            INSERT INTO materials (name, category, force, stress, strain, elasticity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (r["name"] or "Unknown", r["category"] or "Unknown", r["force"] or 0,
              r["stress"] or 0, r["strain"] or 0, r["elasticity"] or 0))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------- DOWNLOAD ----------
@app.route("/download")
def download():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM materials", conn)
    conn.close()
    df.to_excel("materials.xlsx", index=False)
    return send_file("materials.xlsx", as_attachment=True)

# ---------- ADD MATERIAL ----------
@app.route("/add", methods=["POST"])
def add_material():
    name = request.form.get("name")
    category = request.form.get("category")
    force = request.form.get("force", 0)
    stress = request.form.get("stress", 0)
    strain = request.form.get("strain", 0)
    elasticity = request.form.get("elasticity", 0)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO materials (name, category, force, stress, strain, elasticity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, force, stress, strain, elasticity))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------- UPDATE MATERIAL ----------
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_material(id):
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        force = request.form.get("force", 0)
        stress = request.form.get("stress", 0)
        strain = request.form.get("strain", 0)
        elasticity = request.form.get("elasticity", 0)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE materials SET name=?, category=?, force=?, stress=?, strain=?, elasticity=?
            WHERE id=?
        """, (name, category, force, stress, strain, elasticity, id))
        conn.commit()
        conn.close()
        return redirect("/")
    else:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM materials WHERE id=?", (id,))
        material = cur.fetchone()
        conn.close()
        return render_template("update.html", material=material)

# ---------- DELETE MATERIAL ----------
@app.route("/delete/<int:id>")
def delete_material(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM materials WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
