from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://haibadguy.github.io", "https://haibadguy.github.io/pyWebRTC"]}})

# Cấu hình SocketIO
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins=["https://haibadguy.github.io", "https://haibadguy.github.io/pyWebRTC"])

@app.route('/')
def index():
    return "WebRTC Signaling Server is running."

# Xử lý sự kiện "offer" từ client
@socketio.on('offer')
def handle_offer(data):
    print("Received offer:", data)
    emit('answer', {
        'type': 'answer',
        'sdp': data['sdp']  # Giả sử sử dụng chính SDP của client cho logic cơ bản
    }, broadcast=True)

# Xử lý sự kiện "candidate" từ client
@socketio.on('candidate')
def handle_candidate(candidate):
    print("Received ICE candidate:", candidate)
    emit('candidate', candidate, broadcast=True)

# Khi client kết nối
@socketio.on('connect')
def handle_connect():
    print("A client connected.")
    emit('message', {'data': 'Welcome to the WebRTC signaling server!'})

# Khi client ngắt kết nối
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
