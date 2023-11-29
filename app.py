import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import requests

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

database = sqlite3.connect('final_project.db')
db = database.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST": #here it will check the tag with "method = post" and goes on from there

        # Ensure username was submitted
        if not request.form.get("username"):
        #here, the tag in /login path (login.html file in this case) is used to check if text has been input. The "name" element in the html tag is used to link here
            return "Username required"

        # Ensure password was submitted
        elif not request.form.get("password"):
        #here, the tag in /login path (login.html file in this case) is used to check if text has been input. The "name" element in the html tag is used to link here
            return "Password required"

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        users_table = db.execute("SELECT username FROM users")

        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        username = request.form.get("username")

        for name in users_table:
            if name['username'] == username:
                return "username is taken, try a new username"

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password == confirmation:

            hashed_password = generate_password_hash(password) #hashing the password input by the user

            db.execute("INSERT INTO users (username,hash) VALUES(?,?)", username, hashed_password)

            db.close()
            database.close()

            # Redirect user to home page
            return redirect("/")
        else:
            return "passwords entered do not match"

    else:
        return render_template("register.html")

@app.route("/search_cuisine", methods = ["POST"])
def search(): #we will update this, for now we are writing the blueprint
    api_key = "ca38a5949eac429382c9501131ec7d24"
    base_url = "https://api.spoonacular.com/recipes/complexSearch"

    try:
        cuisine = request.form.get("cuisine")
    except:
        print("Error")

    parametres = {
        "apiKey" : api_key,
        "cuisine" : cuisine
    }

    response = requests.get(base_url, parametres)

    if response.status_code == 200:
        data = response.json()
        recipes = [{"title": item["title"], "image": item["image"]} for item in data["results"]]

        return render_template("cuisine.html", recipes = recipes)
    else:
        return f"Error: {response.status_code}"


