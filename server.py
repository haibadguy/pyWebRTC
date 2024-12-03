from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)

# CORS configuration - Adjust for Render URL
CORS(app, resources={r"/*": {"origins": ["https://pywebrtc.onrender.com"]}})

# SocketIO configuration
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins=["https://pywebrtc.onrender.com"])

@app.route('/')
def index():
    return "WebRTC Signaling Server is running."

# Handling 'offer' event from client
@socketio.on('offer')
def handle_offer(data):
    print("Received offer:", data)
    emit('answer', {
        'type': 'answer',
        'sdp': data['sdp']  # Assuming the client sends its SDP as a basic logic
    }, broadcast=True)

# Handling 'candidate' event from client
@socketio.on('candidate')
def handle_candidate(candidate):
    print("Received ICE candidate:", candidate)
    emit('candidate', candidate, broadcast=True)

# When client connects
@socketio.on('connect')
def handle_connect():
    print("A client connected.")
    emit('message', {'data': 'Welcome to the WebRTC signaling server!'})

# When client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")

if __name__ == '__main__':
    # Render automatically sets the port environment variable to PORT
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if no PORT is set
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
