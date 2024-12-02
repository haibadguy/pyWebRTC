from flask import Flask, request, jsonify
from flask_cors import CORS  # Thêm dòng này

app = Flask(__name__)
CORS(app)

# Lưu trữ các phiên kết nối của WebRTC
connections = {}

@app.route('/')
def index():
    return "WebRTC Signaling Server"

# Nhận và lưu offer từ client
@app.route('/offer', methods=['POST'])
def offer():
    data = request.get_json()
    print("Received offer:", data)

    # Giả sử chúng ta tạo một answer cho offer này (trong thực tế bạn sẽ phải tạo một answer dựa trên các logic phức tạp hơn)
    answer = {
        'sdp': 'v=0\r\no=blah 0 0 IN IP4 0.0.0.0\r\ns=blah\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtpmap:96 H264/90000\r\n'
    }
    return jsonify(answer)

# Nhận và xử lý ICE candidate từ client
@app.route('/candidate', methods=['POST'])
def candidate():
    candidate = request.json.get("candidate")
    print("Received candidate:", candidate)
    return jsonify({"status": "Candidate received"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
