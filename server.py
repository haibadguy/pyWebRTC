import ssl
import websockets
import asyncio
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
import json

clients = {}

async def signaling(websocket, path):
    # Nhận thông điệp từ client
    message = await websocket.recv()
    message = json.loads(message)

    if message['type'] == 'offer':
        # Xử lý offer từ client
        offer = RTCSessionDescription(sdp=message['sdp'], type='offer')
        pc = RTCPeerConnection()
        pc_id = "PeerConnection(%s)" % id(pc)
        clients[pc_id] = pc
        await pc.setRemoteDescription(offer)

        # Tạo answer và gửi lại cho client
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        await websocket.send(json.dumps({
            'type': 'answer',
            'sdp': pc.localDescription.sdp
        }))
    elif message['type'] == 'candidate':
        # Xử lý ICE candidate
        candidate = message['candidate']
        for pc in clients.values():
            if pc.remoteDescription:
                await pc.addIceCandidate(candidate)

async def main():
    # Tạo đối tượng SSLContext
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="path/to/cert.pem", keyfile="path/to/key.pem")

    # WebSocket server với SSL
    server = await websockets.serve(signaling, '0.0.0.0', 5000, ssl=ssl_context)
    print("Server started on wss://localhost:5000")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
