document.addEventListener('DOMContentLoaded', (event) => {
    var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);

    // Join the chat room when connected
    socket.on('connect', () => {
        console.log('Connected to server');
        socket.emit('join', { 'username': currentUser });
    });

    // Handle incoming messages
    socket.on('message', (data) => {
        console.log('Received message:', data);
        displayMessage(data.username, data.message);
    });

    // Send a message when the send button is clicked
    document.getElementById('send').onclick = () => {
        let messageInput = document.querySelector('.chat-input input');
        let message = messageInput.value;
        let recipient = document.getElementById('recipient').value;

        if (recipient) {
            console.log('Sending message to', recipient, ':', message);
            socket.emit('message', { 'recipient': recipient, 'message': message });
        } else {
            alert('Please select a chat recipient');
        }

        messageInput.value = '';
    };

    // Search for a user
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

    // Function to get chat requests
    function getChatRequests() {
        fetch('/get_chat_requests')
        .then(response => response.json())
        .then(data => {
            console.log('Chat requests:', data);
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

    // Function to accept a chat request
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

    // Function to reject a chat request
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

    // Function to get accepted chats
    function getAcceptedChats() {
        fetch('/get_accepted_chats')
        .then(response => response.json())
        .then(data => {
            console.log('Accepted chats:', data);
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

    // Function to select a chat
    function selectChat(username) {
        console.log('Selecting chat with', username);
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
            console.log('Messages:', messages);
            let messagesDiv = document.getElementById('chat');
            messages.forEach(msg => {
                displayMessage(msg.username, msg.content);
            });
        });
        document.getElementById('chat-header').textContent = `Chatting with ${username}`;
    }

    // Function to display a message
    function displayMessage(username, message) {
        let messages = document.getElementById('chat');
        let messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';

        let usernameSpan = document.createElement('span');
        usernameSpan.className = 'username';
        usernameSpan.textContent = username + ': ';

        let messageSpan = document.createElement('span');
        messageSpan.className = 'message';
        messageSpan.textContent = message;

        messageDiv.appendChild(usernameSpan);
        messageDiv.appendChild(messageSpan);

        if (username === currentUser) {
            messageDiv.classList.add('sent');
        }

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;  // Auto-scroll to the bottom
    }

    // Initial load
    getChatRequests();
    getAcceptedChats();
});
/* last update : 7/17 1:39pm */ 
