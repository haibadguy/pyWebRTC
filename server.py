from quart import Quart, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription
import logging
import asyncio

app = Quart(__name__)
pcs = set()  # Set to manage peer connections

@app.route('/offer', methods=['POST'])
async def offer():
    params = await request.json
    offer_sdp = params["sdp"]

    # Create new peer connection
    pc = RTCPeerConnection()
    pcs.add(pc)

    # Set remote description
    offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
    await pc.setRemoteDescription(offer)

    # Create answer and set local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Return answer to client
    response = {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
    return jsonify(response)

@app.route('/candidate', methods=['POST'])
async def candidate():
    params = await request.json
    candidate = params["candidate"]

    # Add ICE candidate to all peer connections
    for pc in pcs:
        await pc.addIceCandidate(candidate)
    return jsonify({"status": "ok"})

@app.route('/close', methods=['POST'])
async def close():
    for pc in pcs:
        await pc.close()
    pcs.clear()
    return jsonify({"status": "closed"})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
