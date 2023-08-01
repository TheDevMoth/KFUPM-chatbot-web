localStorage.setItem("messages", JSON.stringify(["Hi! I am KFUPMbot. How can I help you?"]));

function appendMessageToChatbox(message, fromUser) {
    const chatbox = document.getElementById("chatbox");
    const paragraph = document.createElement("p");
    paragraph.innerText = message;
    if (fromUser) {
        paragraph.classList.add("from-user");
    } else {
        paragraph.classList.add("from-bot");
    }
    const arabic = /[\u0600-\u06FF]/;
    if (arabic.test(message)) {
        paragraph.classList.add("arabic");
    }
    chatbox.appendChild(paragraph);
}

// fetch chat response from server
async function fetchChatResponse(messages) {
    const url = "/chat";
    const data = { messages: messages };
    const otherParams = {
        headers: {
            "content-type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify(data),
        method: "POST",
    };
    const response = await fetch(url, otherParams);
    if (!response.ok) {
        const message = `An error has occured: ${response.status}`;
        throw new Error(message);
    }
    console.log(response);
    return response;
}

// sendMessage function adds message to chatbox and fetches response from server
async function sendMessage() {
    let message = document.getElementById("user-input-area").value;
    message = message.trim();
    if (!message) return;
    document.getElementById("user-input-area").value = "";

    // ? should I be maintaining state client-side? seems like a bad idea somehow :\
    let messages = JSON.parse(localStorage.getItem("messages"));
    messages.push(message);

    appendMessageToChatbox(message, true);

    const response = await fetchChatResponse(messages);
    if (response.ok) {
        const data = await response.json();
        appendMessageToChatbox(data.message, false);

        messages.push(data.message);
    }
    localStorage.setItem("messages", JSON.stringify(messages));
}

function expandTextarea(id) {
    document.getElementById(id).addEventListener('keydown', function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        } else {
            this.style.height = 0;
            this.style.height = this.scrollHeight + 'px';
        }
    }, false);
    document.getElementById(id).addEventListener('keyup', function () {
        this.style.height = 0;
        this.style.height = this.scrollHeight + 'px';
    }, false);
}

expandTextarea('user-input-area');