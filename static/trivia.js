// Establish websocket connection to the server in /trivia namespace
var socket = io('http://127.0.0.1:5000/trivia');

// Create synth object to allow Text-to-Speech (TTS)
const synth = window.speechSynthesis;

let score_shown = false; // boolean to check if scores have been shown

// Function to TTS the variable
function speak(text) {
    let utterThis = new SpeechSynthesisUtterance(text);
    utterThis.rate = 0.5;
    synth.speak(utterThis);
};

// Run when user connects to /trivia namespace
socket.on('connected', function(data) { // Receives the list of connected users from the server
    // Track count of online users on connection event
    let length = data.length; // Gets the length of connected users list
    let online_users = document.getElementById("online_users");
    online_users.textContent = `Users online: ${length}`; // Shows the number of online users
});

// Run when user disconnects from /trivia namespace
socket.on('disconnected', function(data) {
    // Track count of online users on disconnection event
    let length = data.length; // Gets the length of connected users list
    let online_users = document.getElementById("online_users");
    online_users.textContent = `Users online: ${length}` // Shows the number of online users
});

// Run when "Start" button is clicked
document.addEventListener("DOMContentLoaded", function() { // Wait for content to fully load
    let start_button = document.getElementById("start_button");
    start_button.addEventListener("click", function() {
        socket.emit("trivia_start"); // Send "trivia_start" event to server to start a trivia round
    });
});

// Run after receiving a question event from the server
socket.on("question", function(data) { // data = question string
    // Remove old scoreboard and reset the score if it's not the first trivia round
    if (score_shown == true) {
        document.getElementById("scores").innerHTML = "";
        score = 0;
        score_shown = false;
    }
    // Render a new question
    let qdiv = document.querySelector(".question");
    qdiv.innerHTML = "" // Delete previous question
    let p = document.createElement("p"); // Create a new question
    p.innerHTML = data;
    qdiv.appendChild(p);

    speak(data); // TTS the question
});

// Disable the answer buttons so user can't send multiple answers
function remove_buttons() {
    buttons = document.querySelectorAll(".answers button");
    buttons.forEach(element => {
        element.disabled = true;
    });
};

let score = 0; // Initialize score to 0 on page load
let answer_input_shown = false; // Boolean to check if answer input box exists

// Run after receiving the answers data from the server
socket.on("answers", function(answers, correct_index) { // answers = list of possible answers; correct_index = index of correct answer
    let alist = document.querySelector(".answers"); // List of rendered answers
    alist.innerHTML = ""; // Clear the previous list of rendered answers

    document.getElementById("correct").textContent = ""; // Clear the "correct"/"incorrect" announcement

    // Create answer input box if it doesn't exist
    if (answer_input_shown == false) {
        answer_div = document.getElementById("answer_div"); 
        answer_input = document.createElement("input");
        answer_div.appendChild(answer_input);
        answer_input.focus();
        answer_input_shown = true;
    };

    answer_input.addEventListener("keyup", function(event) {
        // Announce "correct" if correct answer index is entered to answer input box
        if (event.key == correct_index) {
            let correctness = "Correct"
            speak(correctness); // TTS "Correct"
            document.getElementById("correct").textContent = "Correct";
            score++; // Add 1 to score
        }
        // Announce "incorrect" if incorrect answer index is entered to answer input box
        else {
            let correctness = "Incorrect"
            speak(correctness);
            document.getElementById("correct").textContent = "Incorrect";
        };
        answer_input.remove(); // Remove answer input box
        remove_buttons(); // Remove answer buttons to avoid multiple entries
        answer_input_shown = false;
    });

    // Create a list of answer buttons with corresponding ids
    let i = 1; // Set list count to start from 1
    answers.forEach(element => {
        let li = document.createElement("li");
        let btn = document.createElement("button");
        btn.setAttribute("id", i);
        btn.addEventListener("click", function() {
            let choice = btn.id; // Set user choice to correspond to button id
            
            // Announce "correct"
            if (choice == correct_index) {
                let correctness = "Correct"
                speak(correctness); // TTS "correct"
                document.getElementById("correct").textContent = correctness; // Render "correct"
                score++;
            }
            // Announce "incorrect"
            else {
                let correctness = "Incorrect"
                speak(correctness); // TTS "incorect"
                document.getElementById("correct").textContent = correctness; // Render "incorrect"
            };
            // Remove answer buttons and input box to prevent multiple entries
            remove_buttons();
            answer_input.remove();
            answer_input_shown = false;
        });

        btn.innerHTML = element;
        li.appendChild(btn);
        alist.appendChild(li);

        // TTS answer buttons
        speech = `${i}: ${element}`;
        speak(speech);
        i++; // Increment answer list item index
    });
});

// Send score data after receiving trivia_done event from server
socket.on("trivia_done", function() {
    socket.emit("score", score);
});

// Render scores on page after receiving trivia_scores event and data from server
socket.on("trivia_scores", function(username, score) {
    let scores = document.getElementById("scores");
    let scoreboard = document.createElement("p");
    scoreboard.setAttribute("id", "scoreboard")
    scoreboard.textContent = `${username}: ${score}`;
    scores.appendChild(scoreboard);

    // TTS username and score
    utterThis = `${username} has ${score} points`;
    speak(utterThis);

    score_shown = true;
});