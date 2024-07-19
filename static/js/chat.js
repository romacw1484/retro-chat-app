document.addEventListener('DOMContentLoaded', (event) => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        socket.emit('join', { 'username': currentUser });
    });

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

    document.getElementById('send').onclick = () => {
        let recipientInput = document.getElementById('recipient');
        let messageInput = document.getElementById('message');
        let recipient = recipientInput.value;
        let message = messageInput.value;
        if (recipient) {
            socket.emit('message', { 'recipient': recipient, 'message': message });
        } else {
            alert('Please select a chat recipient');
        }
        messageInput.value = '';
    };

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
