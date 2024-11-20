function toggleChat() {
    var chatWindow = document.getElementById("chatWindow");
    if (chatWindow.style.display === "block") {
        chatWindow.style.display = "none";
    } else {
        chatWindow.style.display = "block";
    }
}

async function sendMessage() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    // Display user's message in the chat window
    const chatBody = document.getElementById("chatBody");
    const userMessage = document.createElement("p");
    userMessage.textContent = "You: " + userInput;
    chatBody.appendChild(userMessage);

    // Clear the input field
    document.getElementById("userInput").value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userInput })
        });
        console.log(response);
        const data = await response.json();
        console.log(data);
        if (data.message) {
            // Display chatbot's response in the chat window
            const botMessage = document.createElement("p");
            botMessage.textContent =data.message;
            botMessage.innerHTML = `Bot: ${marked.parse(data.message)}`;
            chatBody.appendChild(botMessage);
        } else if (data.error) {
            console.error(data.error);
        }

        // Auto-scroll to the bottom of the chat
        chatBody.scrollTop = chatBody.scrollHeight;
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = 'Hi';
recognition.interimResults = false;

// Function to start speech recognition
function startRecognition() {
    recognition.start();
    console.log("Voice recognition started. Speak into the microphone...");
}

// Handle recognition result (user's voice converted to text)
recognition.onresult = function(event) {
    const voiceInput = event.results[0][0].transcript;
    document.getElementById('userInput').value = voiceInput;  // Fill the input field with recognized text
    sendMessage(); // Trigger the chatbot's response based on the recognized text
};

// Error handling
recognition.onerror = function(event) {
    console.error("Speech recognition error: ", event.error);
};


function speak(text) {
    const speech = new SpeechSynthesisUtterance();
    speech.text = text; // The text to speak
    speech.lang = 'Hi'; // Set language
    speech.rate = 1; // Speed of speech
    window.speechSynthesis.speak(speech);
}
