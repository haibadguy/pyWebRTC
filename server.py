from quart import Quart, render_template, request
from quart_cors import cors
from quart_socketio import SocketIO
from aiortc import RTCPeerConnection, RTCSessionDescription
import logging

app = Quart(__name__)
app = cors(app)  # Để hỗ trợ CORS
socketio = SocketIO(app, cors_allowed_origins="*")

pcs = set()

@app.route('/')
async def index():
    return await app.send_static_file('index.html')

@socketio.on('offer')
async def handle_offer(data):
    logging.info("Received offer: %s", data)
    try:
        # Tạo PeerConnection
        pc = RTCPeerConnection()
        pcs.add(pc)

        offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await socketio.emit('answer', {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type,
        })
    except Exception as e:
        logging.error("Error handling offer: %s", e)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
