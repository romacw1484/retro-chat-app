# Retro Chat
<img width="998" alt="Screenshot 2025-02-27 at 6 46 06 PM" src="https://github.com/user-attachments/assets/fc1b4ab2-09d6-448e-af38-73803a8edf1e" />

Retro Chat is a nostalgic, real-time chat application that brings back the classic terminal chat experience. Enjoy a retro-themed interface with real-time messaging, user authentication, and a simple chat request system.

## Features

- **Real-Time Messaging:** Chat with friends instantly using Socket.IO.
- **User Authentication:** Secure login and signup forms with password hashing.
- **Chat Requests:** Send, accept, or reject chat requests.
- **Retro Interface:** Classic terminal-style design with a modern twist.

## Technologies Used

- **Flask** – Python web framework
- **Flask-SocketIO** – Real-time communication
- **Flask-Cors** – Handling cross-origin resource sharing
- **Flask-SQLAlchemy** – ORM for database operations
- **Flask-Migrate** – Database migrations
- **PostgreSQL** – Database (hosted on Railway/Heroku)
- **Gunicorn** – WSGI server for deployment
- **HTML/CSS/JavaScript** – Front-end design

## NOTES

1. Landing/Home Page
- Introduce users to the retro chat experience.
- Brief description of application 
- Options to log in or register
  
2. Login Page
- Allow users to securely sign into their account.
- Retro-styled input fields for username and password
- “Forgot password” link (if applicable)
- Error messages
  
3. Registration/Sign-Up Page
- Enable new users to create an account.
<img width="1034" alt="Screenshot 2025-02-26 at 12 42 36 PM" src="https://github.com/user-attachments/assets/455cece6-7bb2-4496-bd38-ab94a733c504" />

4. Chat Room Page
- Provide the core chat functionality with a nostalgic interface
- Input area for typing messages
- Display of active users and/or channels
<img width="1259" alt="Screenshot 2025-02-26 at 12 43 11 PM" src="https://github.com/user-attachments/assets/38f01935-5374-4a5f-bbc0-65bb47861fec" />

5. Profile/Settings Page (Optional)
- Allow users to view and edit their personal settings.
- Edit personal info (e.g., username, display picture, status message)

Notes:

 - when typing in user to request as friend, you must type their username in correctly 
 - working on some sort of capcha authenfication 
 




