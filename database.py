#making a new database through sqlite3 called final_project
import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
database = sqlite3.connect('final_project.db')

# Create a cursor object to execute SQL queries
db = database.cursor()

# Create a table (if it doesn't exist)
db.execute('''
    CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
 );
''')

# Close the cursor and connection when done
db.close()
database.close()