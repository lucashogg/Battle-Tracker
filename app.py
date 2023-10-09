import os

import sqlite3
from flask import Flask, redirect, render_template, request, session, g
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

key = os.urandom(24)
app.secret_key = key

# Configure database (Per Flask docs)
DATABASE = "battletracker.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show homepage"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html")

        # Query database for username
        rows = query_db(
            "SELECT * FROM users WHERE username = ?",
            [request.form.get("username")],
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Check if username blank
        if not request.form.get("username"):
            return render_template("register.html")

        # Check if password blank
        elif not request.form.get("password"):
            return render_template("register.html")

        # Check if password/confirmation are same
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html")

        else:
            for user in query_db("SELECT username FROM users"):
                if user["username"] == request.form.get("username"):
                    return render_template("register.html")

            # Insert username and password into DB
            cur = get_db().cursor()
            cur.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (
                    request.form.get("username"),
                    generate_password_hash(request.form.get("confirmation")),
                ),
            )
            get_db().commit()
            get_db().close()

            return redirect("/")

    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run()
