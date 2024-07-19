from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO, emit, join_room, leave_room

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# User model with email field
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

class ChatRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Email or username already registered')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/chat')
def chat():
    return render_template('chat.html', username=session['username'])

@app.route('/search_user', methods=['POST'])
def search_user():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'status': 'found', 'user_id': user.id, 'username': user.username})
    else:
        return jsonify({'status': 'not found'})

@app.route('/send_chat_request', methods=['POST'])
def send_chat_request():
    data = request.get_json()
    receiver_id = data['user_id']
    sender_id = session['user_id']
    existing_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
    if not existing_request:
        chat_request = ChatRequest(sender_id=sender_id, receiver_id=receiver_id, status='pending')
        db.session.add(chat_request)
        db.session.commit()
        return jsonify({'status': 'Chat request sent'})
    else:
        return jsonify({'status': 'Chat request already sent'})

@app.route('/get_chat_requests', methods=['GET'])
def get_chat_requests():
    user_id = session['user_id']
    requests = ChatRequest.query.filter_by(receiver_id=user_id, status='pending').all()
    request_list = [{'sender_id': req.sender_id, 'sender_username': User.query.get(req.sender_id).username} for req in requests]
    return jsonify(request_list)

@app.route('/accept_chat_request', methods=['POST'])
def accept_chat_request():
    data = request.get_json()
    sender_id = data['sender_id']
    receiver_id = session['user_id']
    chat_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
    if chat_request:
        chat_request.status = 'accepted'
        db.session.commit()
        return jsonify({'status': 'Chat request accepted'})
    return jsonify({'status': 'Chat request not found'})

@app.route('/reject_chat_request', methods=['POST'])
def reject_chat_request():
    data = request.get_json()
    sender_id = data['sender_id']
    receiver_id = session['user_id']
    chat_request = ChatRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
    if chat_request:
        db.session.delete(chat_request)
        db.session.commit()
        return jsonify({'status': 'Chat request rejected'})
    return jsonify({'status': 'Chat request not found'})

@app.route('/get_accepted_chats', methods=['GET'])
def get_accepted_chats():
    user_id = session['user_id']
    sent_requests = ChatRequest.query.filter_by(sender_id=user_id, status='accepted').all()
    received_requests = ChatRequest.query.filter_by(receiver_id=user_id, status='accepted').all()
    accepted_chats = [{'user_id': req.receiver_id, 'username': User.query.get(req.receiver_id).username} for req in sent_requests]
    accepted_chats += [{'user_id': req.sender_id, 'username': User.query.get(req.sender_id).username} for req in received_requests]
    return jsonify(accepted_chats)

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.get_json()
    recipient_username = data['recipient']
    content = data['message']
    sender_id = session['user_id']
    receiver = User.query.filter_by(username=recipient_username).first()
    if receiver:
        message = Message(sender_id=sender_id, receiver_id=receiver.id, content=content)
        db.session.add(message)
        db.session.commit()
        return jsonify({'status': 'Message saved'})
    return jsonify({'status': 'Recipient not found'})

@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.get_json()
    other_user_username = data['other_user_username']
    other_user = User.query.filter_by(username=other_user_username).first()
    if other_user:
        user_id = session['user_id']
        messages = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user.id)) |
            ((Message.sender_id == other_user.id) & (Message.receiver_id == user_id))
        ).order_by(Message.timestamp).all()
        message_list = [{'username': User.query.get(msg.sender_id).username, 'content': msg.content} for msg in messages]
        return jsonify(message_list)
    return jsonify({'status': 'User not found'})

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        username = session.get('username')
        join_room(user_id)
        emit('status', {'msg': f'{username} has entered the room.'}, room=user_id)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        username = session.get('username')
        leave_room(user_id)
        emit('status', {'msg': f'{username} has left the room.'}, room=user_id)

@socketio.on('message')
def handle_message(data):
    sender_id = session.get('user_id')
    sender_username = session.get('username')
    recipient_username = data.get('recipient')
    message = data.get('message')
    
    receiver = User.query.filter_by(username=recipient_username).first()
    if receiver:
        new_message = Message(sender_id=sender_id, receiver_id=receiver.id, content=message)
        db.session.add(new_message)
        db.session.commit()
        
        # Emit the message to both sender and receiver rooms
        emit('message', {'username': sender_username, 'message': message}, room=receiver.id)
        emit('message', {'username': sender_username, 'message': message}, room=sender_id)

if __name__ == '__main__':
    db.create_all()
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)

# last editied on 7/18  10;37 pm 
