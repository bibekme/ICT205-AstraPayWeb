from flask import Flask, render_template, request, redirect, url_for, session, g
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "hs3UDm5UTKqxy3kG8N39kbx25mc=="
app.debug = True

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "astrapay"),
    "user": os.environ.get("DB_USER", "astrapay"),
    "password": os.environ.get("DB_PASS", "astrapay123"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
}


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            cur.execute(query)
            user = cur.fetchone()
        except Exception as e:
            return render_template("login.html", error=str(e))

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["balance"] = float(user["balance"])
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 10",
        (session["user_id"],),
    )
    transactions = cur.fetchall()

    return render_template(
        "dashboard.html",
        username=session["username"],
        balance=session["balance"],
        transactions=transactions,
    )


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    message = None
    recipient = request.args.get("recipient", "")

    if request.method == "POST":
        recipient = request.form["recipient"]
        amount = request.form["amount"]
        note = request.form["note"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO transactions (user_id, recipient, amount, note) VALUES (%s, %s, %s, %s)",
            (session["user_id"], recipient, amount, note),
        )
        db.commit()
        message = f"Transfer to {recipient} submitted!"

    return render_template(
        "transfer.html",
        username=session["username"],
        balance=session["balance"],
        message=message,
        recipient=recipient,
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == "POST":
        bio = request.form["bio"]
        email = request.form["email"]
        cur.execute(
            "UPDATE users SET bio = %s, email = %s WHERE id = %s",
            (bio, email, session["user_id"]),
        )
        db.commit()

    cur.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()

    return render_template(
        "profile.html",
        user=user,
        username=session["username"],
        balance=session["balance"],
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
