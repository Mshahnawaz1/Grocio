import os
import secrets
import json
import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required


app = Flask(__name__)

# set secret key for flash messages

# app.secret_key = 'your_secret_key'
app.secret_key = secrets.token_hex(32)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///items_list.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
@login_required
def index():

    items = db.execute("SELECT * FROM items WHERE user_id= ?", session["user_id"])
    return render_template("index.html", items=items)


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    category= db.execute("SELECT * FROM category")

    if (request.method == "GET"):
        return render_template("add.html", category=category)
    else:
        book = request.form.get("name")
        # author = request.form.get("author")
        category = request.form.get("category")
        user_id=session["user_id"]
        # for invalid input
        # flash('Success: Input text submitted successfully!', 'success')

        db.execute("INSERT INTO items (name ,category, user_id) VALUES (?, ?, ?)", book, category, user_id)
        # return jsonify(genere)
        flash("Item added successfully!")

        return redirect('/add')


@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        book = request.form.get("book")

    else:
        books_db = db.execute("SELECT DISTINCT(name) FROM books")
        return render_template("contact.html",  books=books_db)

# login and registers

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # hash_bool = check_password_hash(rows[0]["hash"], request.form.get("password"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

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

        user = request.form.get("username")
        password = request.form.get("password")

        # if not user:
        #     return apology("usererror")
        user_num = db.execute(
            "SELECT count(username) AS count FROM users WHERE username=? ", user
        )

        if user_num[0]["count"] != 0:
            return apology("user exist")

        # validate password

        # if not password:
        #     return apology("not pass")
        # elif password != request.form.get("fcpass"):
        #     return apology("no match")

        # store in database

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES ( ? , ?)", user, hash)
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/bmi", methods = ["GET", "POST"])
def bmi():
    return render_template("bmi.html")

if __name__ == "__main__":
    app.run(debug =True)



# delete
@app.route('/delete', methods=['POST'])
def delete_data():
    try:
        data_id = request.json['data_id']

        db.execute("DELETE FROM items WHERE id=?", (data_id,))
        return jsonify({'message': 'Data deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})
