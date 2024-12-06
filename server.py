import asyncio
import json
import logging
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

logging.basicConfig(level=logging.INFO)

class WebRTCServer:
    def __init__(self):
        self.connections = {}

    async def handle_connection(self, websocket, path):
        logging.info(f"New connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "offer":
                    await self.handle_offer(websocket, data)
                elif data["type"] == "answer":
                    await self.handle_answer(websocket, data)
                elif data["type"] == "candidate":
                    await self.handle_candidate(websocket, data)
        except Exception as e:
            logging.error(f"Error handling connection: {e}")
        finally:
            if websocket.remote_address in self.connections:
                del self.connections[websocket.remote_address]

    async def handle_offer(self, websocket, data):
        logging.info("Handling offer")
        offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        peer_connection = RTCPeerConnection()

        @peer_connection.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logging.info(f"ICE connection state changed: {peer_connection.iceConnectionState}")

        await peer_connection.setRemoteDescription(offer)

        answer = await peer_connection.createAnswer()
        await peer_connection.setLocalDescription(answer)

        # Send answer back to the client
        response = {
            "type": "answer",
            "sdp": peer_connection.localDescription.sdp
        }
        await websocket.send(json.dumps(response))

        # Store the peer connection
        self.connections[websocket.remote_address] = peer_connection

    async def handle_answer(self, websocket, data):
        logging.info("Handling answer")
        answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        peer_connection = self.connections.get(websocket.remote_address)
        if peer_connection:
            await peer_connection.setRemoteDescription(answer)
        else:
            logging.error("Peer connection not found")

    async def handle_candidate(self, websocket, data):
        logging.info("Handling candidate")
        candidate = RTCIceCandidate(
            foundation=data["candidate"]["foundation"],
            ip=data["candidate"]["ip"],
            port=data["candidate"]["port"],
            priority=data["candidate"]["priority"],
            protocol=data["candidate"]["protocol"],
            type=data["candidate"]["type"]
        )

        peer_connection = self.connections.get(websocket.remote_address)
        if peer_connection:
            await peer_connection.addIceCandidate(candidate)
        else:
            logging.error("Peer connection not found")

async def main():
    server = WebRTCServer()
    async with websockets.serve(server.handle_connection, "localhost", 8765):
        logging.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run the server forever

if __name__ == "__main__":
    asyncio.run(main())
