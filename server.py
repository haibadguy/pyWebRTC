from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(os.getcwd(), filename)

# Xử lý sự kiện "offer" từ client
@socketio.on('offer')
def handle_offer(data):
    print("Received offer:", data)
    emit('offer', data, broadcast=True)  # Gửi offer lại cho tất cả các client

# Xử lý sự kiện "answer" từ client
@socketio.on('answer')
def handle_answer(data):
    print("Received answer:", data)
    emit('answer', data, broadcast=True)  # Gửi answer lại cho tất cả các client

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
    socketio.run(app, host='0.0.0.0', port=5000)
