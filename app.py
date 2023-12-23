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

api_key = "ca38a5949eac429382c9501131ec7d24"

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
            print(username_sql)
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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search_cuisine", methods = ["POST"])
def search(): #we will update this, for now we are writing the blueprint
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


@app.route("/nutrients_search", methods = ["POST"])
def nutrients_search(): #we will update this, for now we are writing the blueprint
    base_url = "https://api.spoonacular.com/recipes/findByNutrients"

    try:
        calories = request.form.get("calories")
        carbohydrates = request.form.get("carbs")
        protein = request.form.get("protein")
    except:
        return "Error"

    parametres = {
        "apiKey" : api_key,
        "maxCalories" : calories,
        "minProtein" : protein,
        "maxCarbs" : carbohydrates
    }

    response = requests.get(base_url, parametres)

    if response.status_code == 200:
        data = response.json()
        recipes = [{"title": item["title"], "id" : item["id"] , "calories" : item["calories"], "protein" : item["protein"], "carbs" : item["carbs"], "image" : item["image"]} for item in data]
        ## keys we want are title, id, image,calories,protein,fat and carbs
        # get only the id for each reciepe
        recipe_ids = [food["id"] for food in recipes]
        return render_template("nutrients_search.html", recipes = recipes)
        # return recipe_ids
    else:
        return f"Error: {response.status_code}"

# [{"key": value, "key2", value}, {"key" : value, "key2": value} ...]
# result of the query in nutrients_search
# [
#     {
#         "id": 658453,
#         "title": "Roast Pork Florentine With Pomegranate Sauce",
#         "image": "https://spoonacular.com/recipeImages/658453-312x231.jpg",
#         "imageType": "jpg",
#         "calories": 382,
#         "protein": "38g",
#         "fat": "12g",
#         "carbs": "30g"
#     },
#     {
#         "id": 715397,
#         "title": "Cheesy Chicken and Rice Casserole",
#         "image": "https://spoonacular.com/recipeImages/715397-312x231.jpg",
#         "imageType": "jpg",
#         "calories": 464,
#         "protein": "31g",
#         "fat": "28g",
#         "carbs": "21g"
#     }
# ]

@app.route("/get_instructions", methods = ["POST"])
def get_instructions():
    recipe_id = request.form.get("instructions")
    base_url = "https://api.spoonacular.com/recipes/"+ recipe_id +"/analyzedInstructions"
    parametres = {
        "apiKey" : api_key,
    }
    response = requests.get(base_url, parametres)
    if response.status_code == 200:
        data = response.json()

        # Iterate through the recipe data and apply the function
        for recipe in data:
            remove_equipment(recipe.get("steps", []))
            # get("steps", []) tries to retrieve the value associated with the key "steps" from the recipe dictionary.

            # return recipe["steps"]
            # Remove "id" and "localizedName" from ingredients
            modified_recipe_array = [
                {
                    # For each step in the original recipe_array, create a new dictionary
                    "ingredients": [
                        {k: v for k, v in ingredient.items() if k not in ["id", "localizedName"]} for ingredient in step["ingredients"]
                        #k: v for ... if k not in... ->  filters out the "id" and "localizedName" keys from each ingredient dictionary
                        #for ingredient...  iterates over each dictionary in the "ingredients" list of the current step.
                    ],
                    "number": step["number"],
                    "step": step["step"]
                }
                for step in recipe["steps"]
            ]

            array_length = len(modified_recipe_array)

        return render_template("recipe_instructions.html", recipes = modified_recipe_array)
        #wanna go through each iteration on modified_recipe_array so that it's modified_recipe_array[0],modified_recipe_array[1]...modified recipe_array[length-1]
        #modified_recipe_array -> [{"ingredients":[{"name"},{"name"}]}, "number":1, "step":""} , {"ingredients":[{"name"},{"name"}]}, "number":2, "step":""}]

    else:
        return "Food ID typed is not valid"


# function below will remove "equipment" in the respons format inside get_instruction()
def remove_equipment(steps):
    for step in steps:
        step.pop("equipment", None)

# function to remove "localizedName" and "id" from each ingredient
def remove_keys(ingredients):
    for ingredient in ingredients:
        ingredient.pop("localizedName", None)
        ingredient.pop("id", None)

# [
#     {
#         "name": "",
#         "steps":[
#             {
#                 "number": 1,
#                 "step": "Make a marinade of olive oil, pressed garlic, lemon pepper, and Italian seasoning.",
#                 "ingredients": [
#                     {
#                         "id": 1022027,
#                         "name": "italian seasoning",
#                         "localizedName": "italian seasoning",
#                         "image": "dried-herbs.png"
#                     },
#                     {
#                         "id": 1012030,
#                         "name": "lemon pepper",
#                         "localizedName": "lemon pepper",
#                         "image": "seasoning.png"
#                     },
#                     {
#                         "id": 4053,
#                         "name": "olive oil",
#                         "localizedName": "olive oil",
#                         "image": "olive-oil.jpg"
#                     },
#                     {
#                         "id": 0,
#                         "name": "marinade",
#                         "localizedName": "marinade",
#                         "image": "seasoning.png"
#                     },
#                     {
#                         "id": 11215,
#                         "name": "garlic",
#                         "localizedName": "garlic",
#                         "image": "garlic.png"
#                     }
#                 ],
#                 "equipment": []
#             },
#             {
#                 "number": 10,
#                 "step": "Add parmesan as desired.",
#                 "ingredients": [
#                     {
#                         "id": 1033,
#                         "name": "parmesan",
#                         "localizedName": "parmesan",
#                         "image": "parmesan.jpg"
#                     }
#                 ],
#                 "equipment": []
#             }
#         ]
#     }
# ]