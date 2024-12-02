from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Lưu trữ các phiên kết nối của WebRTC
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
    # Giả sử chúng ta tạo một answer cho offer này (trong thực tế bạn sẽ phải tạo một answer dựa trên các logic phức tạp hơn)
    answer = {
        'sdp': 'v=0\r\no=blah 0 0 IN IP4 0.0.0.0\r\ns=blah\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtpmap:96 H264/90000\r\n'
    }
    emit('answer', answer)  # Gửi answer lại cho client

# Sự kiện khi nhận ICE candidate từ client
@socketio.on('candidate')
def handle_candidate(candidate):
    print("Received candidate:", candidate)
    # Tiến hành xử lý candidate nếu cần (ví dụ gửi candidate này cho các client khác)
    emit('candidate', candidate, broadcast=True)  # Gửi candidate này đến tất cả các client khác

# Sự kiện khi một client ngắt kết nối
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected")

if __name__ == '__main__':
    # Chạy server với socketio
    if __name__ == '__main__':
        from gunicorn.app.base import BaseApplication

        class GunicornApp(BaseApplication):
            def __init__(self, app):
                self.app = app
                super().__init__()

            def load(self):
                return self.app

        # Khởi chạy Gunicorn với Flask-SocketIO
        app = socketio.WSGIApp(app)
        GunicornApp(app).run()
