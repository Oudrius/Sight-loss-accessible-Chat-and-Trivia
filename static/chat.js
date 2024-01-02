// Establish websocket connection to the server in /chat namespace
var socket = io.connect('http://127.0.0.1:5000/chat');

// Create synth object to allow Text-to-Speech (TTS)
const synth = window.speechSynthesis;


// Get messages from the input and send to server
document.addEventListener("DOMContentLoaded", function() { // Prevent from script running too early
    let messageBox = document.getElementById("message_box")
    messageBox.addEventListener("keyup", function(event) { // Send message by clicking "Enter"
        if (event.key == "Enter") {
            let message = messageBox.value;
            socket.emit("message", message); // Send message to server
            messageBox.value = ""; // Clear message input box
        };
    });
});

// Create a list of connected usernames
function myFunction(value) {
    let li = document.createElement("li");
    let ul = document.getElementById("users_connected");
    li.appendChild(document.createTextNode(value));
    ul.appendChild(li);
};

// Run when server confirms connection
socket.on('connected', function(data) {
    let ul = document.getElementById("users_connected");
    ul.innerHTML = ''; // Empty the previous list of connected users
    data.forEach(myFunction); // Create a list of connected usernames
});

// Run when server confirms disconnection
socket.on('disconnected', function(data) {
    let ul = document.getElementById("users_connected");
    ul.innerHTML = ''; // Empty the previous list of connected users
    data.forEach(myFunction); // Create a list of connected usernames
});

// Run after receiving a message from the server
socket.on('message', function(message, username) {
    
    // Create a list of messages with usernames
    let response_box = document.querySelector("#chatbox_responses");
    let li = document.createElement("li");

    let response = `${username}: ${message}`; // Fornat new entry
    // Append new list element to the list of chat messages
    li.appendChild(document.createTextNode(response));
    response_box.appendChild(li);

    // TTS username and message
    voiceMessage = `${username} says ${message}`;
    let utterThis = new SpeechSynthesisUtterance(voiceMessage);
    synth.speak(utterThis);
});