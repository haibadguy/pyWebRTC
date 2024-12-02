from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')  # frontend của bạn

@socketio.on('offer')
def handle_offer(offer):
    # Xử lý offer từ client
    emit('offer', offer, broadcast=True)

@socketio.on('answer')
def handle_answer(answer):
    # Xử lý answer từ client
    emit('answer', answer, broadcast=True)

@socketio.on('ice-candidate')
def handle_ice_candidate(candidate):
    # Xử lý ICE candidate từ client
    emit('ice-candidate', candidate, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
