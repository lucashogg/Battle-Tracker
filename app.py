import os

import sqlite3
from flask import Flask, redirect, render_template, request, session, g
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

key = os.urandom(24)
app.secret_key = key


# Configure SQLite database
con = sqlite3.connect("battletracker.db")
con.row_factory = sqlite3.Row
cur = con.cursor()


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
    """Show portfolio of stocks"""
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
        rows = cur.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
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


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """Register user"""
#     if request.method == "POST":
#         # Check if username blank
#         if not request.form.get("username"):
#             return render_template("register.html")

#         # Check if password blank
#         elif not request.form.get("password"):
#             return render_template("register.html")

#         # Check if password/confirmation are same
#         elif request.form.get("password") != request.form.get("confirmation"):
#             return render_template("register.html")

#         else:
#             all_users = db.execute("SELECT username FROM users")
#             for user in all_users:
#                 if user["username"] == request.form.get("username"):
#                     return render_template("register.html")

#             # Insert username and password into DB
#             db.execute(
#                 "INSERT INTO users (username, hash) VALUES (?, ?)",
#                 request.form.get("username"),
#                 generate_password_hash(request.form.get("confirmation")),
#             )

#             return redirect("/")

#     else:
#         return render_template("register.html")

if __name__ == "__main__":
    app.run()
