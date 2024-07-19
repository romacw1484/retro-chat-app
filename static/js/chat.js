document.addEventListener('DOMContentLoaded', (event) => {
    // Connect to the Socket.IO server
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // When the user connects, emit a join event with the username
    socket.on('connect', () => {
        socket.emit('join', { 'username': currentUser });
    });

    // Listen for incoming messages and display them in the chat box
    socket.on('message', (data) => {
        let messages = document.getElementById('chat');
        let message = document.createElement('div');
        message.className = 'chat-message';

        let usernameSpan = document.createElement('span');
        usernameSpan.className = 'username';
        usernameSpan.textContent = data.username + ': ';
        
        let messageSpan = document.createElement('span');
        messageSpan.className = 'message';
        messageSpan.textContent = data.message;

        message.appendChild(usernameSpan);
        message.appendChild(messageSpan);

        if (data.username === currentUser) {
            message.classList.add('sent');
        }

        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;  // Auto-scroll to the bottom
    });

    // Function to send a message
    function sendMessage() {
        let messageInput = document.querySelector('.chat-input input');
        let message = messageInput.value;
        let recipient = document.querySelector('.chat-header').textContent.split(' ')[2]; // Adjust this line as per your implementation
        if (recipient && message) {
            socket.emit('message', { 'recipient': recipient, 'message': message });
            messageInput.value = '';
        } else {
            alert('Please select a chat recipient and type a message.');
        }
    }

    // Send a message when the send button is clicked
    document.querySelector('.chat-input button').onclick = sendMessage;

    // Send a message when the enter key is pressed
    document.querySelector('.chat-input input').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Search for users when the search button is clicked
    document.getElementById('search-button').onclick = () => {
        let username = document.getElementById('search-user').value;
        fetch('/search_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username })
        })
        .then(response => response.json())
        .then(data => {
            let userList = document.getElementById('user-list');
            userList.innerHTML = '';
            if (data.status === 'found') {
                let userItem = document.createElement('div');
                userItem.className = 'search-result';
                
                let userNameSpan = document.createElement('span');
                userNameSpan.textContent = data.username;

                let requestButton = document.createElement('button');
                requestButton.textContent = 'Request';
                requestButton.className = 'button-30 request-button';
                requestButton.onclick = () => {
                    sendChatRequest(data.user_id);
                    requestButton.textContent = 'Sent';
                    requestButton.style.backgroundColor = 'gray';
                };

                userItem.appendChild(userNameSpan);
                userItem.appendChild(requestButton);
                userList.appendChild(userItem);
            } else {
                alert('User not found');
            }
        });
    };

    // Function to send a chat request
    function sendChatRequest(userId) {
        fetch('/send_chat_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
            getChatRequests();
        });
    }

    // Get chat requests and display them
    function getChatRequests() {
        fetch('/get_chat_requests')
        .then(response => response.json())
        .then(data => {
            let chatRequests = document.getElementById('chat-requests');
            chatRequests.innerHTML = '';
            data.forEach(request => {
                let requestItem = document.createElement('div');
                requestItem.className = 'chat-request-item';
                requestItem.textContent = `${request.sender_username} wants to chat with you`;
                let acceptButton = document.createElement('button');
                acceptButton.textContent = 'Accept';
                acceptButton.className = 'button-30 accept-button';
                acceptButton.onclick = () => acceptChatRequest(request.sender_id);
                let rejectButton = document.createElement('button');
                rejectButton.textContent = 'Reject';
                rejectButton.className = 'button-30 reject-button';
                rejectButton.onclick = () => rejectChatRequest(request.sender_id);
                requestItem.appendChild(acceptButton);
                requestItem.appendChild(rejectButton);
                chatRequests.appendChild(requestItem);
            });
        });
    }

    // Accept a chat request
    function acceptChatRequest(senderId) {
        fetch('/accept_chat_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender_id: senderId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
            getChatRequests();
            getAcceptedChats();
        });
    }

    // Reject a chat request
    function rejectChatRequest(senderId) {
        fetch('/reject_chat_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender_id: senderId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
            getChatRequests();
        });
    }

    // Get accepted chats and display them
    function getAcceptedChats() {
        fetch('/get_accepted_chats')
        .then(response => response.json())
        .then(data => {
            let chatList = document.getElementById('chat-list');
            chatList.innerHTML = '';
            data.forEach(chat => {
                let chatItem = document.createElement('div');
                chatItem.className = 'friend-item';
                chatItem.textContent = chat.username;
                chatItem.onclick = () => selectChat(chat.username);
                chatList.appendChild(chatItem);
            });
        });
    }

    // Select a chat and load messages
    function selectChat(username) {
        document.getElementById('recipient').value = username;
        document.getElementById('recipient').readOnly = true;
        document.getElementById('chat').innerHTML = '';  // Clear previous messages
        fetch('/get_messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ other_user_username: username })
        })
        .then(response => response.json())
        .then(messages => {
            let messagesDiv = document.getElementById('chat');
            messages.forEach(msg => {
                let message = document.createElement('div');
                message.className = 'chat-message';
                if (msg.username === currentUser) {
                    message.classList.add('sent');
                }
                let usernameSpan = document.createElement('span');
                usernameSpan.className = 'username';
                usernameSpan.textContent = msg.username + ': ';
                let messageSpan = document.createElement('span');
                messageSpan.className = 'message';
                messageSpan.textContent = msg.content;
                message.appendChild(usernameSpan);
                message.appendChild(messageSpan);
                messagesDiv.appendChild(message);
            });
            messagesDiv.scrollTop = messagesDiv.scrollHeight;  // Auto-scroll to the bottom
        });
        document.getElementById('chat-header').textContent = `Chatting with ${username}`;
    }

    // Initial load
    getChatRequests();
    getAcceptedChats();
});

/* last update : 7/17 1:39pm */ 
