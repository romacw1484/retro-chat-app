from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify  # Import necessary Flask modules
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy for database handling
from werkzeug.security import generate_password_hash, check_password_hash  # Import functions for password hashing
from dotenv import load_dotenv, find_dotenv  # Import modules to handle environment variables
import os  # Import os module to interact with the operating system
from flask_socketio import SocketIO, emit, join_room, leave_room  # Import SocketIO for real-time communication
from flask_migrate import Migrate  # Import Flask-Migrate for handling database migrations

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set secret key for session management

# Parse the database URL from DATABASE_URL environment variable
uri = os.getenv('RAILWAY_DATABASE_URL')
print(f"Database URL: {uri}")  # Debugging line to print database URL
if uri and uri.startswith("postgres://"):  # Check if the URL starts with 'postgres://'
    uri = uri.replace("postgres://", "postgresql://", 1)  # Replace it with 'postgresql://'

app.config['SQLALCHEMY_DATABASE_URI'] = uri  # Set database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications for SQLAlchemy
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the app
migrate = Migrate(app, db)  # Initialize Flask-Migrate with the app and database
socketio = SocketIO(app)  # Initialize SocketIO with the app

# Define User model
class User(db.Model):
    __tablename__ = 'users'  # Update table name if needed
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    username = db.Column(db.String(150), nullable=False, unique=True)  # Username column
    password = db.Column(db.String(150), nullable=False)  # Password column
    email = db.Column(db.String(150), nullable=False, unique=True)  # Email column

# Define ChatRequest model
class ChatRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to user id
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to user id
    status = db.Column(db.String(50), nullable=False, default='pending')  # Status column

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to user id
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to user id
    content = db.Column(db.String(500), nullable=False)  # Content column
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Timestamp column

@app.route('/')
def home():
    return render_template('login.html')  # Render login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Check if the request method is POST
        username = request.form['username']  # Get username from form
        password = request.form['password']  # Get password from form
        user = User.query.filter_by(username=username).first()  # Query user by username
        if user and check_password_hash(user.password, password):  # Check if user exists and password matches
            session['user_id'] = user.id  # Set user id in session
            session['username'] = user.username  # Set username in session
            return redirect(url_for('chat'))  # Redirect to chat page
        else:
            flash('Invalid credentials')  # Flash invalid credentials message
            return redirect(url_for('login'))  # Redirect to login page
    return render_template('login.html')  # Render login page

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':  # Check if the request method is POST
        username = request.form['username']  # Get username from form
        password = request.form['password']  # Get password from form
        email = request.form['email']  # Get email from form
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()  # Query user by email or username
        if existing_user:  # Check if user already exists
            flash('Email or username already registered')  # Flash user already registered message
            return redirect(url_for('signup'))  # Redirect to signup page
        hashed_password = generate_password_hash(password, method='sha256')  # Hash the password
        new_user = User(username=username, password=hashed_password, email=email)  # Create new user
        db.session.add(new_user)  # Add new user to the session
        db.session.commit()  # Commit the session
        return redirect(url_for('login'))  # Redirect to login page
    return render_template('signup.html')  # Render signup page

@app.route('/chat')
def chat():
    return render_template('chat.html', username=session['username'])  # Render chat page with username

@app.route('/search_user', methods=['POST'])
def search_user():
    data = request.get_json()  # Get JSON data from request
    username = data.get('username')  # Get username from JSON data
    user = User.query.filter_by(username=username).first()  # Query user by username
    if user:  # Check if user exists
        return jsonify({'status': 'found', 'user_id': user.id, 'username': user.username})  # Return user data
    else:
        return jsonify({'status': 'not found'})  # Return not found status

@app.route('/send_chat_request', methods=['POST'])
def send_chat_request():
    data = request.get_json()  # Get JSON data from request
    receiver_id = data['user_id']  # Get receiver id from JSON data
    sender_id = session['user_id']  # Get sender id from session
    existing_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()  # Query existing chat request
    if not existing_request:  # Check if chat request does not exist
        chat_request = ChatRequest(sender_id=sender_id, receiver_id=receiver_id, status='pending')  # Create new chat request
        db.session.add(chat_request)  # Add chat request to the session
        db.session.commit()  # Commit the session
        return jsonify({'status': 'Chat request sent'})  # Return chat request sent status
    else:
        return jsonify({'status': 'Chat request already sent'})  # Return chat request already sent status

@app.route('/get_chat_requests', methods=['GET'])
def get_chat_requests():
    user_id = session['user_id']  # Get user id from session
    requests = ChatRequest.query.filter_by(receiver_id=user_id, status='pending').all()  # Query pending chat requests
    request_list = [{'sender_id': req.sender_id, 'sender_username': User.query.get(req.sender_id).username} for req in requests]  # Create list of chat requests
    return jsonify(request_list)  # Return chat requests

@app.route('/accept_chat_request', methods=['POST'])
def accept_chat_request():
    data = request.get_json()  # Get JSON data from request
    sender_id = data['sender_id']  # Get sender id from JSON data
    receiver_id = session['user_id']  # Get receiver id from session
    chat_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()  # Query chat request
    if chat_request:  # Check if chat request exists
        chat_request.status = 'accepted'  # Update chat request status
        db.session.commit()  # Commit the session
        return jsonify({'status': 'Chat request accepted'})  # Return chat request accepted status
    return jsonify({'status': 'Chat request not found'})  # Return chat request not found status

@app.route('/reject_chat_request', methods=['POST'])
def reject_chat_request():
    data = request.get_json()  # Get JSON data from request
    sender_id = data['sender_id']  # Get sender id from JSON data
    receiver_id = session['user_id']  # Get receiver id from session
    chat_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()  # Query chat request
    if chat_request:  # Check if chat request exists
        db.session.delete(chat_request)  # Delete chat request
        db.session.commit()  # Commit the session
        return jsonify({'status': 'Chat request rejected'})  # Return chat request rejected status
    return jsonify({'status': 'Chat request not found'})  # Return chat request not found status

@app.route('/get_accepted_chats', methods=['GET'])
def get_accepted_chats():
    user_id = session['user_id']  # Get user id from session
    sent_requests = ChatRequest.query.filter_by(sender_id=user_id, status='accepted').all()  # Query sent accepted chat requests
    received_requests = ChatRequest.query.filter_by(receiver_id=user_id, status='accepted').all()  # Query received accepted chat requests
    accepted_chats = [{'user_id': req.receiver_id, 'username': User.query.get(req.receiver_id).username} for req in sent_requests]  # Create list of sent accepted chats
    accepted_chats += [{'user_id': req.sender_id, 'username': User.query.get(req.sender_id).username} for req in received_requests]  # Add list of received accepted chats
    return jsonify(accepted_chats)  # Return accepted chats

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.get_json()  # Get JSON data from request
    recipient_username = data['recipient']  # Get recipient username from JSON data
    content = data['message']  # Get message content from JSON data
    sender_id = session['user_id']  # Get sender id from session
    receiver = User.query.filter_by(username=recipient_username).first()  # Query receiver by username
    if receiver:  # Check if receiver exists
        message = Message(sender_id=sender_id, receiver_id=receiver.id, content=content)  # Create new message
        db.session.add(message)  # Add message to the session
        db.session.commit()  # Commit the session
        return jsonify({'status': 'Message saved'})  # Return message saved status
    return jsonify({'status': 'Recipient not found'})  # Return recipient not found status

@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.get_json()  # Get JSON data from request
    other_user_username = data['other_user_username']  # Get other user username from JSON data
    other_user = User.query.filter_by(username=other_user_username).first()  # Query other user by username
    if other_user:  # Check if other user exists
        user_id = session['user_id']  # Get user id from session
        messages = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user.id)) |
            ((Message.sender_id == other_user.id) & (Message.receiver_id == user_id))
        ).order_by(Message.timestamp).all()  # Query messages between users
        message_list = [{'username': User.query.get(msg.sender_id).username, 'content': msg.content} for msg in messages]  # Create list of messages
        return jsonify(message_list)  # Return messages
    return jsonify({'status': 'User not found'})  # Return user not found status

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')  # Get user id from session
    if user_id:  # Check if user id exists
        username = session.get('username')  # Get username from session
        join_room(user_id)  # Join user to room
        emit('status', {'msg': f'{username} has entered the room.'}, room=user_id)  # Emit status message

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')  # Get user id from session
    if user_id:  # Check if user id exists
        username = session.get('username')  # Get username from session
        leave_room(user_id)  # Remove user from room
        emit('status', {'msg': f'{username} has left the room.'}, room=user_id)  # Emit status message

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")  # Debug statement to print received message
    sender_id = session.get('user_id')  # Get sender id from session
    sender_username = session.get('username')  # Get sender username from session
    recipient_username = data.get('recipient')  # Get recipient username from data
    message = data.get('message')  # Get message content from data
    
    receiver = User.query.filter_by(username=recipient_username).first()  # Query receiver by username
    if receiver:  # Check if receiver exists
        new_message = Message(sender_id=sender_id, receiver_id=receiver.id, content=message)  # Create new message
        db.session.add(new_message)  # Add message to the session
        db.session.commit()  # Commit the session
        
        print(f"Message saved: {message}")  # Debug statement to print saved message
        
        # Emit the message to both sender and receiver rooms
        emit('message', {'username': sender_username, 'message': message}, room=receiver.id)  # Emit message to receiver room
        emit('message', {'username': sender_username, 'message': message}, room=sender_id)  # Emit message to sender room

if __name__ == '__main__':
    db.create_all()  # Create all database tables
    port = int(os.environ.get('PORT', 5001))  # Get port from environment or use default 5001
    socketio.run(app, debug=True, host='0.0.0.0', port=port)  # Run the app with SocketIO on the specified port
