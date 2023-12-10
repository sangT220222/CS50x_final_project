import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required

import requests

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

database = sqlite3.connect('final_project.db', check_same_thread=False)
db = database.cursor()

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST": #here it will check the tag with "method = post" and goes on from there

        retrieved_username = request.form.get("username")
        retrieved_password = request.form.get("password")
        # Ensure username was submitted
        if not retrieved_username:
        #here, the tag in /login path (login.html file in this case) is used to check if text has been input. The "name" element in the html tag is used to link here
            return "Username required"

        # Ensure password was submitted
        elif not retrieved_password:
        #here, the tag in /login path (login.html file in this case) is used to check if text has been input. The "name" element in the html tag is used to link here
            return "Password required"

        try:
            # Getting the username and password from the database based on user's input
            username_sql = db.execute("SELECT * FROM users WHERE username = ?", (retrieved_username,)).fetchone()
            db.close()
            # username_sql will return (id, username, hashed_passowrd)
        except Exception as e:
             return "Invalid username. Please try again"
            # check_password_hash(hashed_password, plain password) -> returns bool

        if check_password_hash(username_sql[2], retrieved_password):
        # Remember which user has logged in
            session["user_id"] = username_sql[0] #result = (id,username,password), as the schema of the database query is known, hence result[0] was utilised here
        else:
            return "Invalid password. Please try again"



        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":

        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirmation = request.form.get("confirmation")


        # Ensure username/password are submitted
        if not new_username or not new_password or not confirmation:
            return "Must provide username/password/confirm password"

        users_result = db.execute("SELECT username FROM users").fetchall()
        # users_results = [('test',), ('test2',)] for eg
        for username in users_result:
            if username[0] == new_username:
                return "Username has been taken. Please try another one."
        if not new_password == confirmation:
            return "Passwords provided do not match"

        db.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (new_username, generate_password_hash(new_password)))
        database.commit()
        db.close()
        return redirect("/")

    return render_template("register.html")

@app.route("/change_password", methods=["GET"])
def change_password():
        return render_template("change_password.html")

@app.route("/update_password", methods = ["POST"])
def update_password():
        #get relevant information from the corresponding HTML fields
        username = request.form.get("username")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        try:    #checking if provided username is in the database
            information = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        except Exception as e:
            return "Sorry, provided username is not in our system."

        #checks for password matching with the system or not
        if not check_password_hash(information[2], old_password):
            return "Wrong password provided."

        #checks if 2 provided new passwords match each oterh
        if new_password != confirm_password:
            return "New passwords provided do not match."

        #updating the desired username's password on the system
        db.execute("UPDATE users SET hashed_password = (?) where username = (?)", (generate_password_hash(new_password), username))
        database.commit()
        db.close()

        return redirect("/")

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


