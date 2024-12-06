import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE

# Khởi tạo Flask app và SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
logging.basicConfig(level=logging.INFO)

pcs = set()  # Lưu các PeerConnection đang hoạt động

@app.route('/')
def index():
    """Trả về file index.html"""
    return send_from_directory(os.getcwd(), 'index.html')

@socketio.on('offer')
async def handle_offer(data):
    """Xử lý SDP offer từ client"""
    try:
        sdp = data.get('sdp')
        type_ = data.get('type')

        if not sdp or not type_:
            socketio.emit('error', {'error': 'Invalid SDP or type'})
            return

        # Tạo PeerConnection
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("icecandidate")
        def on_icecandidate(event):
            """Lắng nghe các ICE candidate"""
            if event.candidate:
                socketio.emit('candidate', {'candidate': event.candidate.to_dict()})
            else:
                logging.info("Đã gửi hết các ICE candidate")

        @pc.on("track")
        def on_track(track):
            """Xử lý track từ remote peer"""
            logging.info(f"Đã nhận track: {track.kind}")
            if track.kind == "video":
                logging.info("Xử lý track video")
            elif track.kind == "audio":
                logging.info("Xử lý track audio")

        # Đặt SDP và tạo SDP answer
        offer = RTCSessionDescription(sdp, type_)
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        # Trả SDP answer cho client
        socketio.emit('answer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        })
    except Exception as e:
        logging.error(f"Xảy ra lỗi: {e}")
        socketio.emit('error', {'error': 'Lỗi xử lý offer'})

@socketio.on('candidate')
async def handle_candidate(data):
    """Xử lý ICE candidate từ client"""
    try:
        candidate = data.get('candidate')
        if candidate:
            pc = next(iter(pcs))
            await pc.addIceCandidate(candidate)
    except Exception as e:
        logging.error(f"Xảy ra lỗi: {e}")

@socketio.on('cleanup')
def cleanup():
    """Đóng tất cả các kết nối PeerConnection"""
    logging.info("Dọn dẹp các kết nối PeerConnection")
    for pc in pcs:
        pc.close()
    pcs.clear()
    socketio.emit('cleanup_done', {'status': 'Đã dọn dẹp'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # PORT từ biến môi trường
    socketio.run(app, host='0.0.0.0', port=port)
