import os

import sqlite3
import random
from flask import Flask, redirect, render_template, request, session, g, flash
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


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show homepage"""

    # Grab currrent battle characters
    current_battle = query_db(
        "SELECT * FROM current_battle WHERE user_id = ? ORDER BY initiative DESC",
        [session["user_id"]],
    )
    # Grab currrent users characters
    chars = query_db(
        "SELECT * FROM characters WHERE user_id = ?",
        [session["user_id"]],
    )

    cond = [
        "BLINDED",
        "CHARMED",
        "DEAFENED",
        "EXHAUSTION",
        "FRIGHTENED",
        "GRAPPLED",
        "INCAPACITATED",
        "INVISIBLE",
        "PARALYZED",
        "PETRIFIED",
        "POISONED",
        "PRONE",
        "RESTRAINED",
        "STUNNED",
        "UNCOUNSCIOUS",
    ]

    # Select character from dropdown
    if request.method == "POST":
        char = query_db(
            "SELECT * FROM characters WHERE user_id = ? AND name = ?",
            [session["user_id"], request.form.get("char-select")],
        )

        battle_char = query_db(
            "SELECT * FROM current_battle WHERE user_id = ? AND name = ?",
            [session["user_id"], request.form.get("char-select")],
        )

        if not battle_char:
            for data in char:
                cur = get_db().cursor()
                cur.execute(
                    "INSERT INTO current_battle (name, ac, max_hp, current_hp, modifier, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        data["name"],
                        data["ac"],
                        data["max_hp"],
                        data["current_hp"],
                        data["modifier"],
                        session["user_id"],
                    ),
                )
                get_db().commit()
                get_db().close()

            return redirect("/")

        else:
            flash("Character aleady in battle session")

    return render_template(
        "index.html", current_battle=current_battle, chars=chars, cond=cond
    )


@app.route("/battle", methods=["GET", "POST"])
@login_required
def battle():
    """Battle actions"""
    if request.method == "POST":
        # Delete a character from battle
        if request.form["battle"] == "deletechar":
            cur = get_db().cursor()
            cur.execute(
                "DELETE FROM current_battle WHERE user_id = ? AND name = ?",
                [session["user_id"], request.form.get("deletechar")],
            )
            get_db().commit()
            get_db().close()

        # Update current HP
        elif request.form["battle"] == "damage":
            damage = request.form.get("damage")
            name = request.form.get("currenthp")

            current_hp = query_db(
                "SELECT current_hp FROM current_battle WHERE user_id = ? AND name = ?",
                [session["user_id"], name],
            )

            max_hp = query_db(
                "SELECT max_hp FROM current_battle WHERE user_id = ? AND name = ?",
                [session["user_id"], name],
            )

            for data in current_hp:
                new_hp = data["current_hp"] + int(damage)
                if new_hp < 0:
                    new_hp = 0
                elif new_hp > max_hp[0]["max_hp"]:
                    new_hp = max_hp[0]["max_hp"]

                cur = get_db().cursor()
                cur.execute(
                    "UPDATE current_battle SET current_hp = ? WHERE user_id = ? AND name = ?",
                    [
                        new_hp,
                        session["user_id"],
                        name,
                    ],
                )
                get_db().commit()
                get_db().close()

        return redirect("/")

    return redirect("/")


@app.route("/initiative", methods=["POST"])
@login_required
def initiative():
    modifier = query_db(
        "SELECT modifier, name FROM current_battle WHERE user_id = ?",
        [session["user_id"]],
    )

    # chars = []
    # initiative = int(data["modifier"]) + random.randint(1, 20)

    for data in modifier:
        initiative = int(data["modifier"]) + random.randint(1, 20)
        # dict = {"name": data["name"], "init": initiative}
        # chars.append(dict)
        name = data["name"]

        cur = get_db().cursor()
        cur.execute(
            "UPDATE current_battle SET initiative = ? WHERE user_id = ? AND name = ?",
            [
                initiative,
                session["user_id"],
                name,
            ],
        )
        get_db().commit()
    get_db().close()

    return redirect("/")


@app.route("/currenthp", methods=["POST"])
@login_required
def currenthp():
    """Update current hp"""
    damage = request.form.get("damage")
    name = request.form.get("currenthp")

    current_hp = query_db(
        "SELECT current_hp FROM current_battle WHERE user_id = ? AND name = ?",
        [session["user_id"], name],
    )

    for data in current_hp:
        new_hp = data["current_hp"] + int(damage)

        cur = get_db().cursor()
        cur.execute(
            "UPDATE current_battle SET current_hp = ? WHERE user_id = ? AND name = ?",
            [
                new_hp,
                session["user_id"],
                name,
            ],
        )
        get_db().commit()
        get_db().close()

    return redirect("/")


@app.route("/condition", methods=["POST"])
@login_required
def condition():
    """Update character condition"""
    name = request.form.get("char-select")
    condition = request.form.get("condition")

    cond = query_db(
        "SELECT condition FROM current_battle WHERE user_id = ? AND name = ?",
        [session["user_id"], name],
    )

    for data in cond:
        if request.form["cond"] == "add":
            if data["condition"] != condition:
                cur = get_db().cursor()
                cur.execute(
                    "UPDATE current_battle SET condition = ? WHERE user_id = ? AND name = ?",
                    [
                        condition,
                        session["user_id"],
                        name,
                    ],
                )
                get_db().commit()
                get_db().close()

        elif request.form["cond"] == "remove":
            if data["condition"] == condition:
                cur = get_db().cursor()
                cur.execute(
                    "UPDATE current_battle SET condition = ? WHERE user_id = ? AND name = ?",
                    [
                        None,
                        session["user_id"],
                        name,
                    ],
                )
                get_db().commit()
                get_db().close()

    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    error = None
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Invalid credentials"

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Invalid credentials"

        else:
            # Query database for username
            user = query_db(
                "SELECT * FROM users WHERE username = ?",
                [request.form.get("username")],
                one=True,
            )
            # Ensure username exists and password is correct
            if user is None or not check_password_hash(
                user["hash"], request.form.get("password")
            ):
                error = "Invalid credentials"

            else:
                # Remember which user has logged in
                session["user_id"] = user["id"]

                # Redirect user to home page
                return redirect("/")

        return render_template("login.html", error=error)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", error=error)


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
    error = None
    if request.method == "POST":
        # Check if username blank
        if not request.form.get("username"):
            error = "Invalid credentials"

        # Check if password blank
        elif not request.form.get("password"):
            error = "Invalid credentials"

        # Check if password/confirmation are same
        elif request.form.get("password") != request.form.get("confirmation"):
            error = "Invalid credentials"

        else:
            # Check if user already exists
            user = query_db(
                "SELECT username FROM users WHERE username = ?",
                [request.form.get("username")],
                one=True,
            )

            # If user doesn't exister, ceate new user
            if user is None:
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

            # If user exists, print error
            else:
                error = "Select a different user name"

        return render_template("register.html", error=error)

    else:
        return render_template("register.html")


@app.route("/characters", methods=["GET", "POST"])
@login_required
def characters():
    """Character page"""

    # Grab currrent users characters
    chars = query_db(
        "SELECT * FROM characters WHERE user_id = ?",
        [session["user_id"]],
    )

    # Select character from dropdown
    if request.method == "POST":
        char = query_db(
            "SELECT * FROM characters WHERE user_id = ? AND name = ?",
            [session["user_id"], request.form.get("char-select")],
        )

        return render_template("characters.html", char=char, chars=chars)

    return render_template("characters.html", chars=chars)


@app.route("/edit", methods=["POST"])
@login_required
def edit():
    """Character edit function"""

    # Get values from inputs
    charname = request.form.get("charname")
    armorclass = request.form.get("armorclass")
    maxhp = request.form.get("maxhp")
    currenthp = request.form.get("currenthp")
    modifier = request.form.get("modifier")

    # Make sure at least one field (and positive values) is entered
    if (
        not charname
        and (not armorclass or int(armorclass) < 1)
        and (not maxhp or int(maxhp) < 1)
        and (not currenthp or int(currenthp) < 0)
        and (not modifier or int(modifier) < 0)
    ):
        flash("At least one field must be filled out or enter only positve values")

    # Update character in database
    else:
        if charname:
            cur = get_db().cursor()
            cur.execute(
                "UPDATE characters SET name = ? WHERE user_id = ? and name = ?",
                (
                    charname,
                    session["user_id"],
                    request.form.get("edit"),
                ),
            )

        if armorclass:
            cur = get_db().cursor()
            cur.execute(
                "UPDATE characters SET ac = ? WHERE user_id = ? and name = ?",
                (
                    armorclass,
                    session["user_id"],
                    request.form.get("edit"),
                ),
            )

        if maxhp:
            cur = get_db().cursor()
            cur.execute(
                "UPDATE characters SET max_hp = ? WHERE user_id = ? and name = ?",
                (
                    maxhp,
                    session["user_id"],
                    request.form.get("edit"),
                ),
            )

        if currenthp:
            cur = get_db().cursor()
            cur.execute(
                "UPDATE characters SET current_hp = ? WHERE user_id = ? and name = ?",
                (
                    currenthp,
                    session["user_id"],
                    request.form.get("edit"),
                ),
            )

        if modifier:
            cur = get_db().cursor()
            cur.execute(
                "UPDATE characters SET modifier = ? WHERE user_id = ? and name = ?",
                (
                    modifier,
                    session["user_id"],
                    request.form.get("edit"),
                ),
            )

        get_db().commit()
        get_db().close()

        flash("Character Successfully Edited")

    return redirect("/characters")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add character page"""

    if request.method == "POST":
        # Check if fields are left blank
        if not request.form.get("charname"):
            flash("Must enter character name")

        elif (
            not request.form.get("armorclass")
            or int(request.form.get("armorclass")) < 1
        ):
            flash("Must enter armor class")

        elif not request.form.get("maxhp") or int(request.form.get("maxhp")) < 1:
            flash("Must enter max hp")

        elif (
            not request.form.get("currenthp") or int(request.form.get("currenthp")) < 0
        ):
            flash("Must enter current hp")

        elif not request.form.get("modifier") or int(request.form.get("modifier")) < 0:
            flash("Must enter modifier")

        else:
            # Check if character name exists
            char = query_db(
                "SELECT name FROM characters WHERE user_id = ? AND name = ?",
                [session["user_id"], request.form.get("charname")],
                one=True,
            )

            if char is None:
                # If name is unique, add to db
                cur = get_db().cursor()
                cur.execute(
                    "INSERT INTO characters (name, ac, max_hp, current_hp, modifier, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        request.form.get("charname"),
                        request.form.get("armorclass"),
                        request.form.get("maxhp"),
                        request.form.get("currenthp"),
                        request.form.get("modifier"),
                        session["user_id"],
                    ),
                )
                get_db().commit()
                get_db().close()

                flash("Character Successfully Added")

                return render_template("add.html")

            else:
                flash("Character name already taken")

        return render_template("add.html")

    return render_template("add.html")


@app.route("/removechar", methods=["POST"])
@login_required
def removechar():
    """Delete character from database"""
    cur = get_db().cursor()
    cur.execute(
        "DELETE FROM characters WHERE user_id = ? AND name = ?",
        [session["user_id"], request.form.get("remove-char")],
    )
    get_db().commit()
    get_db().close()

    flash("Character Successfully Deleted")

    return redirect("/characters")


if __name__ == "__main__":
    app.run()
