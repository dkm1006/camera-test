
import socket
from threading import Event

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

HOST = '0.0.0.0'
PORT = 8554
FRAME_SIZE = (640, 480)
FORMAT = 'XRGB8888'
BITRATE = 10000000

def error_callback(e):
    event.set()


def main():
    pc = Picamera2()
    video_config = pc.create_video_configuration({"size": FRAME_SIZE, 'format': FORMAT})
    pc.configure(video_config)

    encoder = H264Encoder(bitrate=BITRATE)
    encoder.audio = False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))

        while True:
            print("Waiting")
            sock.listen()

            conn, addr = sock.accept()
            print("Connected")

            output = PyavOutput(f"pipe:{conn.fileno()}", format="mpegts")
            # output = PyavOutput("rtsp://127.0.0.1:8554/cam", format="rtsp") only with MediaMTX
            # output = PyavOutput("udp://<ip-addr>:<port>", format="mpegts")
            event = Event()
            output.error_callback = error_callback

            pc.start_recording(encoder, output)

            event.wait()
            print("Disconnected")

            pc.stop_recording()


if __name__ = '__main__':
    main()