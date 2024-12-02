from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Cấu hình CORS, cho phép tất cả các origin hoặc chỉ một số origin cụ thể
CORS(app, origins=["https://haibadguy.github.io"], supports_credentials=True)

# Cấu hình SocketIO
socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index():
    return "WebRTC Signaling Server"

# Sự kiện khi một client kết nối
@socketio.on('connect')
def handle_connect():
    print("A client connected")
    emit('message', {'data': 'Welcome to the WebRTC Signaling Server!'})

# Sự kiện khi nhận offer từ client
@socketio.on('offer')
def handle_offer(data):
    print("Received offer:", data)
    answer = {
        'sdp': 'v=0\r\no=blah 0 0 IN IP4 0.0.0.0\r\ns=blah\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtpmap:96 H264/90000\r\n'
    }
    emit('answer', answer)

# Sự kiện khi nhận ICE candidate từ client
@socketio.on('candidate')
def handle_candidate(candidate):
    print("Received candidate:", candidate)
    emit('candidate', candidate, broadcast=True)

# Sự kiện khi một client ngắt kết nối
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
