import websockets
import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription

clients = {}

async def signaling(websocket, path):
    try:
        # Nhận thông điệp từ client
        message = await websocket.recv()
        message = json.loads(message)

        if message['type'] == 'offer':
            # Xử lý offer từ client
            offer = RTCSessionDescription(sdp=message['sdp'], type='offer')
            pc = RTCPeerConnection()
            pc_id = f"PeerConnection({id(pc)})"
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
    except Exception as e:
        print(f"Error handling WebSocket message: {e}")
    finally:
        # Đảm bảo loại bỏ client sau khi kết thúc
        await websocket.close()

async def main():
    # Tạo WebSocket server
    server = await websockets.serve(signaling, "0.0.0.0", 5000)
    print("Server started on ws://localhost:5000")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
