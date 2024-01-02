from cs50 import SQL
from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit, namespace
from werkzeug.security import check_password_hash, generate_password_hash

import requests
import json
import time
import threading
import random

from helpers import login_required

# Initialize Flask application
app = Flask(__name__)

# Configure Socket.IO to work with Flask application
socketio = SocketIO(app)

# Configure Session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure app to use sqlite database
db = SQL("sqlite:///chat.db")

# Keep a list of connected users
connected_users_chat = []
connected_users_trivia = []

# Ensure browser doesn't cache the app
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Execute when user connects to a chat namespace
@socketio.on('connect', namespace='/chat')
def handle_connect():
    # Get username from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # Append username to a list of connected usernames
    connected_users_chat.append(username)
    # Emit connection to client
    socketio.emit("connected", connected_users_chat, namespace='/chat')

# Execute when user disconnects from a chat namespace
@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    # Get username from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # Remove username from a list of connected usernames
    connected_users_chat.remove(username)
    # Emit disconnection to client
    socketio.emit("disconnected", connected_users_chat, namespace='/chat')

# Execute when client emits a message from the chat namespace
@socketio.on('message', namespace='/chat')
def handle_message(message):
    # Get username from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # Emit message and username from server to client
    socketio.emit("message", (message, username), namespace='/chat')
    print(f'message: {username, message}')

# Execute when user connects to a trivia namespace
@socketio.on('connect', namespace='/trivia')
def handle_connect():
    # Get username from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # Append username to a list of connected usernames
    connected_users_trivia.append(username)
    # Emit connection to client
    socketio.emit("connected", connected_users_trivia, namespace='/trivia')

# Execute when user disconnects from a trivia namespace
@socketio.on('disconnect', namespace='/trivia')
def handle_disconnect():
    # Get username from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # Remove username from a list of connected usernames
    connected_users_trivia.remove(username)
    # Emit disconnection to client
    socketio.emit("disconnected", connected_users_trivia, namespace='/trivia')


# Define index route
@app.route("/")
def index():
    return redirect("/chat")

# Define register route
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    # On "GET" request
    if request.method == "GET":
        return render_template("register.html")
    
    # On "POST" request
    elif request.method == "POST":
        username = request.form.get("username") # Get username input
        password = request.form.get("password") # Get password input
        db_usernames = db.execute("SELECT username FROM users") # Get a list of all usernames in db

        # Fill the list of all usernames in database
        usernames = []
        for row in db_usernames:
            usernames.append(row["username"])

        # Flash error if username is blank
        if not username:
            error = 'Enter a username'
            return render_template("register.html", error=error)

        # Flash error if username contains special characters
        elif not username.isalnum():
            error = 'Username cannot contain special characters'
            return render_template("register.html", error=error)

        # Flash error if username length is invalid
        elif len(username) <= 3 or len(username) >= 9:
            error = 'Username should be 4 - 8 characters long'
            return render_template("register.html", error=error)

        # Flash error if username already exists
        elif username in usernames:
            error = 'Username already exists'
            return render_template("register.html", error=error)

        # Flash error if password is empty
        elif not password:
            error = 'Enter a password'
            return render_template("register.html", error=error)

        # Flash error if password length is invalid
        elif len(password) <= 5 or len(password) >= 13:
            error = 'Password should be 6 - 12 characters long'
            return render_template("register.html", error=error)

        # Execute if conditions are met
        else:
            # Hash password
            hash = generate_password_hash(password, method="pbkdf2", salt_length=16)

            # Insert new user data to database
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, hash)

            return redirect("/")

# Define login route
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget existing user_id
    session.clear()
    # Set error message to none
    error = None

    # On "GET" request
    if request.method == "GET":
        return render_template("login.html")

    # On "POST" request
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Flash error if username is blank
        if not username:
            error = 'Enter a username'
            return render_template("login.html", error=error)

        # Flash error if somebody tries to enter a long username
        elif len(username) >= 9:
            error = 'Username does not exist'
            return render_template("login.html", error=error)

        # Flash error if password is blank
        elif not password:
            error = 'Enter a password'
            return render_template("login.html", error=error)

        # Flash error if somebody tries to enter a long password
        elif len(password) >= 13:
            error = 'Incorrect password'
            return render_template("login.html", error=error)
        
        else:
            # Get data from users table in db
            user_data = db.execute("SELECT * FROM users WHERE username = ?", username)

            # Check if username exists and password is correct
            if len(user_data) != 1 or not check_password_hash(user_data[0]["password_hash"], password):
                error = 'Incorrect username and/or password'
                return render_template("login.html", error=error)
            
            # Execute if conditions are met
            else:
                # Set session id to be same as user's id in db
                session["user_id"] = user_data[0]["id"]

                return redirect("/")

# Define logout route
@app.route("/logout")
def logout():

    # Forget user_id
    session.clear()

    return redirect("/")

# Define chat route
@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html")

# Define trivia route
@app.route("/trivia")
@login_required
def trivia():
    return render_template("trivia.html")

# Execute after receiving trivia_start event from client
@socketio.on("trivia_start", namespace="/trivia")
def trivia_start():

    # Thread callback function (when timer stops)
    def timeout_callback():
        print("Time's up!")

    # Thread function to start the timer
    def start_timer(seconds, callback):
        print(f"Timer started for {seconds} seconds.")
        time.sleep(seconds)
        callback()

    # Get trivia data from opentdb API
    url = 'https://opentdb.com/api.php?amount=2'
    response = requests.get(url)


    if response.status_code == 200:

        # Send questions and answers to the client
        dict = json.loads(response.text)["results"] # Decode JSON-f string to Python object

        for row in dict:
            socketio.emit("question", row['question'], namespace="/trivia") # Send question to client
            # Append correct and incorrect answers to answers list and shuffle it
            answers = []
            answers.append(row['correct_answer'])
            for i in row['incorrect_answers']:
                answers.append(i)
            random.shuffle(answers)

            correct_index = answers.index(row['correct_answer']) + 1 # Get the index of correct answer in a new list
            print(correct_index)
            socketio.emit('answers', (answers, correct_index), namespace="/trivia") # Emit the answers list and index of correct answer to client

            # Create a thread to time the questions
            timer = threading.Thread(target=start_timer, args=(20, timeout_callback))
            timer.start() # Start a thread
            timer.join() # Wait for thread to finish before going to the next row
        socketio.emit("trivia_done", namespace="/trivia") # Signal to client that question/answer round is done

    # Print to server that trivia data could not be reached through API
    else:
        print("Unable to get trivia data.")

# Execute after receiving score from client
@socketio.on("score", namespace="/trivia")
def score(data):
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"] # Get the client username based on their session id
    score = data # Set the client's score
    socketio.emit("trivia_scores", (username, score), namespace="/trivia") # Send username and score to client

# Host the flask server on localhost
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
