import asyncio
from flask import Flask, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay, MediaPlayer, MediaRecorder
import logging

# Flask app for signaling
app = Flask(__name__)

# Relay for forwarding media streams
relay = MediaRelay()

# Peer connection instances
pcs = set()


# Route to handle offer from the client
@app.route('/offer', methods=['POST'])
async def offer():
    params = request.json
    offer_sdp = params["sdp"]

    # Create a new peer connection
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        print(f"Received track: {track.kind}")
        # Forward the track using a relay or process it
        if track.kind == "video":
            relay.subscribe(track)

    # Set remote description (SDP from client)
    offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
    await pc.setRemoteDescription(offer)

    # Create answer and set it as local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send answer back to the client
    response = {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
    return jsonify(response)


# Route to handle ICE candidates
@app.route('/candidate', methods=['POST'])
async def candidate():
    params = request.json
    candidate = params["candidate"]

    # Add ICE candidate to all peer connections
    for pc in pcs:
        await pc.addIceCandidate(candidate)
    return jsonify({"status": "ok"})


# Cleanup peer connections
@app.route('/close', methods=['POST'])
def close():
    for pc in pcs:
        asyncio.run(pc.close())
    pcs.clear()
    return jsonify({"status": "closed"})


# Run the Flask app
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
