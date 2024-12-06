from quart import Quart, request
from quart_cors import cors
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Quart and Socket.IO
app = Quart(__name__)
app = cors(app, allow_origin="*")
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app_asgi = socketio.ASGIApp(sio, app)

pcs = set()  # Track active PeerConnections

@app.route("/")
async def index():
    return "WebRTC Server is running!"

@sio.on("offer")
async def handle_offer(sid, data):
    logging.info("Received offer: %s", data)
    try:
        pc = RTCPeerConnection()
        pcs.add(pc)

        # Set remote description
        offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        await pc.setRemoteDescription(offer)

        # Create answer and send it to the client
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await sio.emit("answer", {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }, room=sid)

        # Handle ICE candidates
        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await sio.emit("candidate", {"candidate": candidate.to_json()}, room=sid)
                logging.info("Sent candidate: %s", candidate)

    except Exception as e:
        logging.error("Error handling offer: %s", e)

@sio.on("candidate")
async def handle_candidate(sid, data):
    """Handle ICE candidates from the client."""
    try:
        candidate = data.get("candidate")
        if candidate:
            logging.info("Received candidate: %s", candidate)
            for pc in pcs:
                await pc.addIceCandidate(candidate)
    except Exception as e:
        logging.error("Error handling candidate: %s", e)

@sio.on("cleanup")
async def handle_cleanup(sid):
    """Cleanup resources when the client disconnects."""
    logging.info("Cleaning up resources.")
    for pc in pcs:
        await pc.close()
    pcs.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=5000)
