import sqlite3

def login(user_input):
    query = "SELECT * FROM users WHERE username = '" + user_input + "'"
    conn = sqlite3.connect("users.db")
    conn.execute(query)