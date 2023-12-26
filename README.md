Flask, Python, HTML, CSS, SQLITE3 are used to complete a website that will provide personalised reciepe for users. Users will be able to login and provide details to have tailored cuisine provided.


app.py: Handles user authentication, interacts with an SQLite database, and integrates with the Spoonacular API to provide recipe-related functionalities in a web application. It utilizes the Spoonacular API to search for recipes based on cuisine and nutrient values. Additionally it uses Werkzeug to hash and check passwords securely. And Jinja templating is used to dynamically generate HTML content based on data received from the server.

helper.py: contains decorator - login_required, used to protect routes in a web application. If a user is not logged in, the decorator redirects them to the login page. Otherwise, it allows access to the protected route. 

database.py: code that created database clled final_project with desired datababse layout.

final_project.db: this is the database used to store users' login information.

static/: this folder contains the css files that are used with the respective html pages. 

templates/: this folder contains all the html pages that are used for this project.

Website preview:
![image](https://github.com/sangT220222/CS50x_final_project/assets/100322380/710df68a-8ed4-4f11-88b0-43a8f3c33a16)
