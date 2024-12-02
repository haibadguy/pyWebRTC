import logging
import asyncio
from quart import Quart, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription
import hypercorn.asyncio
from hypercorn.config import Config

# Tạo ứng dụng Quart
app = Quart(__name__)
pcs = set()  # Set để quản lý peer connections

# Route cho offer
@app.route('/offer', methods=['POST'])
async def offer():
    params = await request.json()
    offer_sdp = params["sdp"]

    # Tạo peer connection mới
    pc = RTCPeerConnection()
    pcs.add(pc)

    # Thiết lập remote description
    offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
    await pc.setRemoteDescription(offer)

    # Tạo answer và thiết lập local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Trả về answer cho client
    response = {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
    return jsonify(response)

# Route cho ICE candidate
@app.route('/candidate', methods=['POST'])
async def candidate():
    params = await request.json()
    candidate = params["candidate"]

    # Thêm ICE candidate vào tất cả peer connections
    for pc in pcs:
        await pc.addIceCandidate(candidate)
    return jsonify({"status": "ok"})

# Route để đóng kết nối
@app.route('/close', methods=['POST'])
async def close():
    # Đóng tất cả các peer connections
    for pc in pcs:
        await pc.close()
    pcs.clear()
    return jsonify({"status": "closed"})

# Main entry point cho ứng dụng
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Cấu hình Hypercorn (ASGI server)
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    
    # Chạy ứng dụng với Hypercorn
    hypercorn.asyncio.serve(app, config)
