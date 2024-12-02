from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet

# Sử dụng eventlet để chạy server socket
eventlet.monkey_patch()

app = Flask(__name__)

# Cho phép CORS chỉ cho domain https://haibadguy.github.io
CORS(app, origins="https://haibadguy.github.io") 

socketio = SocketIO(app, async_mode='eventlet')  # Sử dụng eventlet để xử lý đồng thời

# Lưu trữ các kết nối WebRTC
connections = {}

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
    # Giả sử chúng ta tạo một SDP answer (trong thực tế cần thêm các logic khác)
    answer = {
        'sdp': 'v=0\r\no=blah 0 0 IN IP4 0.0.0.0\r\ns=blah\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtpmap:96 H264/90000\r\n'
    }
    emit('answer', answer)  # Gửi answer lại cho client

# Sự kiện khi nhận ICE candidate từ client
@socketio.on('candidate')
def handle_candidate(candidate):
    print("Received candidate:", candidate)
    # Tiến hành xử lý candidate và gửi cho tất cả các client khác
    emit('candidate', candidate, broadcast=True)

# Sự kiện khi một client ngắt kết nối
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected")

if __name__ == '__main__':
    # Chạy server SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
