import asyncio
import json
import logging
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from websockets import serve

logging.basicConfig(level=logging.INFO)

# Lớp xử lý kết nối WebRTC
class WebRTCSignaling:
    def __init__(self):
        self.connections = {}

    async def handle_connection(self, websocket, path):
        logging.info(f"New connection from {websocket.remote_address}")

        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "offer":
                    # Xử lý offer và tạo peer connection
                    await self.handle_offer(websocket, data)
                elif data["type"] == "answer":
                    # Xử lý answer
                    await self.handle_answer(websocket, data)
                elif data["type"] == "candidate":
                    # Xử lý ICE candidate
                    await self.handle_candidate(websocket, data)
        except Exception as e:
            logging.error(f"Error handling connection: {e}")
        finally:
            # Đảm bảo đóng kết nối khi kết thúc
            if websocket.remote_address in self.connections:
                del self.connections[websocket.remote_address]

    async def handle_offer(self, websocket, data):
        logging.info("Received offer")
        offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        pc = RTCPeerConnection()
        pc_id = f"PeerConnection({websocket.remote_address})"
        self.connections[websocket.remote_address] = pc

        @pc.on("icecandidate")
        def on_icecandidate(candidate):
            if candidate:
                logging.info(f"Sending ICE candidate to {websocket.remote_address}")
                candidate_data = candidate.to_dict()
                asyncio.create_task(websocket.send(json.dumps({
                    "type": "candidate",
                    "candidate": candidate_data
                })))

        await pc.setRemoteDescription(offer)

        # Tạo và gửi answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        await websocket.send(json.dumps({
            "type": "answer",
            "sdp": pc.localDescription.sdp
        }))

    async def handle_answer(self, websocket, data):
        logging.info("Received answer")
        answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        pc = self.connections.get(websocket.remote_address)
        if pc:
            await pc.setRemoteDescription(answer)

    async def handle_candidate(self, websocket, data):
        logging.info("Received ICE candidate")
        candidate_data = data["candidate"]
        candidate = RTCIceCandidate(
            foundation=candidate_data["foundation"],
            component=candidate_data["component"],
            transport=candidate_data["transport"],
            priority=candidate_data["priority"],
            ip=candidate_data["ip"],
            port=candidate_data["port"],
            type=candidate_data["type"],
            raddr=candidate_data.get("raddr", ""),
            rport=candidate_data.get("rport", 0),
            generation=candidate_data["generation"],
            ufrag=candidate_data["ufrag"],
            network_id=candidate_data["network-id"],
            network_cost=candidate_data["network-cost"]
        )
        pc = self.connections.get(websocket.remote_address)
        if pc:
            await pc.addIceCandidate(candidate)

# Chạy WebSocket server
async def main():
    signaling = WebRTCSignaling()
    async with serve(signaling.handle_connection, "localhost", 8765):
        logging.info("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # Keep the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
