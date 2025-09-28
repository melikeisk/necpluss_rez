from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import USERS, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı modeli
class QueueEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# Ana sayfa → guest
@app.route("/")
def home():
    return redirect(url_for("guest"))

# Guest ekranı
@app.route("/guest", methods=["GET", "POST"])
def guest():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            entry = QueueEntry(name=name)
            db.session.add(entry)
            db.session.commit()
        return redirect(url_for("guest"))

    queue = QueueEntry.query.all()
    return render_template("guest.html", queue=queue)

# Login ekranı
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in USERS and USERS[username] == password:
            session["username"] = username
            session["role"] = "admin"
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Kullanıcı adı veya şifre yanlış!")

    return render_template("login.html")

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("guest"))

# Admin ekranı
@app.route("/index", methods=["GET", "POST"])
def index():
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        if "add" in request.form:
            name = request.form.get("add", "").strip()
            if name:
                db.session.add(QueueEntry(name=name))
                db.session.commit()
        elif "delete" in request.form:
            try:
                idx = int(request.form.get("delete"))
                entry = QueueEntry.query.get(idx)
                if entry:
                    db.session.delete(entry)
                    db.session.commit()
            except:
                pass
        elif "clear" in request.form:
            QueueEntry.query.delete()
            db.session.commit()
        return redirect(url_for("index"))

    queue = QueueEntry.query.all()
    return render_template("index.html", queue=queue, username=session["username"])

if __name__ == "__main__":
    app.run(debug=True)
