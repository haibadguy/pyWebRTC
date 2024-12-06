from quart import Quart, render_template, request
from quart_cors import cors
from quart_socketio import SocketIO
from aiortc import RTCPeerConnection, RTCSessionDescription
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

app = Quart(__name__)
app = cors(app, allow_origin="*")  # Hỗ trợ CORS
socketio = SocketIO(app, cors_allowed_origins="*")

pcs = set()  # Quản lý các PeerConnection

@app.route('/')
async def index():
    return await app.send_static_file('index.html')

@socketio.on('offer')
async def handle_offer(data):
    """Xử lý SDP offer từ client."""
    logging.info("Received offer: %s", data)
    try:
        # Tạo PeerConnection
        pc = RTCPeerConnection()
        pcs.add(pc)

        # Đặt remote SDP
        offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
        await pc.setRemoteDescription(offer)

        # Tạo answer và gửi lại client
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await socketio.emit('answer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type,
        })
        logging.info("Sent answer: %s", pc.localDescription.sdp)

        # Xử lý ICE candidate từ server
        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await socketio.emit("candidate", {"candidate": candidate.to_json()})
                logging.info("Sent candidate: %s", candidate)

    except Exception as e:
        logging.error("Error handling offer: %s", e)

@socketio.on('candidate')
async def handle_candidate(data):
    """Xử lý ICE candidate từ client."""
    try:
        candidate = data.get("candidate")
        if candidate:
            logging.info("Received candidate: %s", candidate)
            for pc in pcs:
                await pc.addIceCandidate(candidate)
    except Exception as e:
        logging.error("Error handling candidate: %s", e)

@socketio.on('cleanup')
async def handle_cleanup():
    """Dọn dẹp tài nguyên khi client kết thúc."""
    logging.info("Cleaning up resources.")
    for pc in pcs:
        await pc.close()
    pcs.clear()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
