# Sight-loss accessible Chat and Trivia
#### Video Demo:  <https://www.youtube.com/watch?v=qM7fkSPpyLo>
#### Description:
Sight-loss accessible Chat and Trivia is a final project for CS50x course. It is a prototype web app that features two main functionalities - real time chat and trivia. It is a prototype app and is not meant to be deployed and/or used for the general public.

The purposes of making this app were:

- Get more practise on the material learned in CS50x course
- Learn new technologies beyond what CS50x has to offer
- Demonstrate the use of all used tools in action

The focus of this project was mainly accessibility features and back-end. This web-app was made having sight-loss population in mind. For these reasons, barely any styling has been done.

#### Tools

- Back-end
  + Python with Flask
  + Flask SocketIO (for network sockets)
  + Flask session
  + Open Trivia DB API (for trivia questions)
  + Multithreading (to time trivia rounds)
  + Werkzeug Security (for password hashing)

- Front-end
  + HTML
  + CSS
  - Javascript
    + SocketIO
    + Speeck Synthesis (for Text-to-Speech)

- Database
  + SQLite3 database engine
  + CS50 SQL library for Python 

- Templating engine
  + Jinja

#### Files' purposes

- app.py
  + runs the server
  + handles HTTP requests
  + configures use of filesystem for sessions
  + manages password security
  + manages database queries
  + controls network socket connections
  + keeps lists of connected users
  + handles messages between server and client
  + handles API request to Open Trivia DB
  + handles real-time trivia logic

- helpers.py
  + contains function that is used to enfore login requirement on cerain routes

- chat.db
  + database containing id, username and password hash

- requirements.txt
  + documents dependencies and their versions used in the project

- static/styles.css
  + contains style properties for all of the html files

- static/chat.js
  + adds dynamic features to /chat route
  + handles network socket connections and events
  + handles Text-to-Speech
  + listens for users' messages and renders them
  + shows the list of connected users

- static/trivia.js
  + adds dynamic features to /trivia route
  + handles network socket connections and events
  + renders trivia questions and answers received from the server
  + renders score
  + handles Text-to-Speech
  + records score and sends it to server
  + receives and renders usernames and connected user count

- templates/layout.html
  + contains the html layout
  + contains Jinja syntax (applies to other html elements as well)

- templates/chat.html
  + contains the html for /chat route

- templates/login.html
  + contains the html for /login route

- templates/register.html
  + contains the html for /register route

- templates/trivia.html
  + contais the html for /trivia route