from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["https://haibadguy.github.io"])

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

    # Tạo SDP answer với thời gian 't=' hợp lệ
    answer = {
        'type': 'answer',
        'sdp': 'v=0\r\no=blah 0 0 IN IP4 0.0.0.0\r\ns=blah\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\nt=0 0\r\na=rtpmap:96 H264/90000\r\na=setup:actpass\r\n'  # Đảm bảo 't=0 0' có mặt
    }

    # Gửi answer lại cho client
    emit('answer', answer, broadcast=True)

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
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
