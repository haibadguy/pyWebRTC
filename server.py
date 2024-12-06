import os
import logging
from quart import Quart, jsonify, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription
from quart_cors import cors

# Khởi tạo ứng dụng Quart
app = Quart(__name__)
app = cors(app)

logging.basicConfig(level=logging.INFO)

# Quản lý các kết nối PeerConnection
pcs = set()

@app.route('/')
async def index():
    return await send_from_directory(os.getcwd(), 'index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    try:
        params = await request.get_json()
        if not params or 'sdp' not in params or 'type' not in params:
            return jsonify({'error': 'Invalid request'}), 400

        # Tạo PeerConnection
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on('icecandidate')
        async def on_icecandidate(event):
            if event.candidate:
                logging.info('New ICE candidate: %s', event.candidate)
            else:
                logging.info('All ICE candidates have been sent.')

        @pc.on('track')
        async def on_track(track):
            logging.info('Received track: %s', track.kind)

        # Đặt SDP từ offer và tạo answer
        offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
        await pc.setRemoteDescription(offer)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        logging.info("Generated SDP answer for the offer.")

        return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})
    except Exception as e:
        logging.error("Error processing offer: %s", e)
        return jsonify({'error': 'Failed to process offer'}), 500

@app.route('/cleanup', methods=['POST'])
async def cleanup():
    logging.info("Cleaning up peer connections.")
    for pc in pcs:
        await pc.close()
    pcs.clear()
    return jsonify({'status': 'Cleaned up'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
