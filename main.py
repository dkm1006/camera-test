import cv2
from picamera2 import Picamera2
import time

DEST_IP = '0.0.0.0'
DEST_PORT = '8554'

def init_video_capture():
    """Initialize video capture"""
    pc = Picamera2()
    pc.configure(pc.create_video_configuration(
        main={
            # "format": "YUV420",  # this gives an image in gray with multiple smaller versions underneath, shape 720, 640
            "format": "XRGB8888",
            "size": (640, 480)
        })
    )
    pc.start()
    return pc


def init_video_writer(output_str="output.mp4", fourcc_str='MP4V'):
    """Video writer initialization with explicit FPS"""
    save_fps = 15.0  # Adjust this based on your actual processing speed
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)  # one of MP4V, XVID, MJPG, X264
    out = cv2.VideoWriter(output_str, fourcc, save_fps, (640, 480))
    return out


def init_video_streamer(output_url=f"udp://{DEST_IP}:{DEST_PORT}?pkt_size=1316"):
    """Video streamer"""
    # TODO: FFMPEG cannot stream directly over the network. Gstreamer could,
    #       but OpenCV is not compiled with support out of the box. 
    #       Therefore, it would have to be compiled from source with Gstreamer enabled.
    #
    # git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/opencv/opencv-python.git
    # cd opencv-python
    # export CMAKE_ARGS="-DWITH_GSTREAMER=ON"
    # export ENABLE_CONTRIB=0
    # export ENABLE_HEADLESS=0
    # uv pip wheel . --verbose
    # uv
    save_fps = 15.0  # Adjust this based on your actual processing speed
    fourcc = cv2.VideoWriter_fourcc(*"MP4V")  # one of MP4V, XVID, MJPG, X264
    out = cv2.VideoWriter(output_url, fourcc, save_fps, (640, 480))
    print(f"✅ Streaming to {output_url} ... Press Ctrl+C to stop.")
    return out


def get_frame(capture):
    frame = capture.capture_array() 
    frame = cv2.flip(frame, 1)
    # print("Frame:", frame.shape) 
    return frame #.copy()


def obtain_user_command(default=None):
    key = cv2.waitKey(1) & 0xFF
    key2command = {
        ord("t"): "threshold",
        ord("e"): "edge",
        ord("s"): "bg_sub",
        ord("c"): "contour",
        ord("n"): "normal",
        ord("q"): "quit",
        ord("r"): "red",
        ord("g"): "green",
        ord("b"): "blue",
        ord("i"): "infrared" 
    }
    command = key2command.get(key, default)
    return command


capture = init_video_capture()
out = init_video_writer(output_str="output.mp4")
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

print('Video output is open:', out.isOpened())

# Current mode
mode = "normal"
# FPS calculation
prev_time = time.time()

while True:
    frame = get_frame(capture)
    # print(f"Captured frame of size {frame.shape}")
    if mode == "red":
        frame = cv2.cvtColor(frame[:,:,0], cv2.COLOR_GRAY2BGR)
 
    elif mode == "green":
        frame = cv2.cvtColor(frame[:,:,1], cv2.COLOR_GRAY2BGR)
 
    elif mode == "blue":
        frame = cv2.cvtColor(frame[:,:,2], cv2.COLOR_GRAY2BGR)
 
    elif mode == "infrared":
        frame = cv2.cvtColor(frame[:,:,3], cv2.COLOR_GRAY2BGR)
 
    elif mode == "threshold":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, frame = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
 
    elif mode == "edge":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
 
    elif mode == "bg_sub":
        fg_mask = bg_subtractor.apply(frame)
        frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
 
    elif mode == "contour":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
 
    # Calculate actual processing FPS
    curr_time = time.time()
    processing_fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
 
    # Display actual processing FPS
    cv2.putText(
        frame, f"FPS: {int(processing_fps)} Mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )
 
    # Write frame to video
    out.write(frame)
 
    # Show video
    cv2.imshow("Live Video", frame)
    # print('Video output is open:', out.isOpened())
    mode = obtain_user_command(mode)
    if mode == "quit":
        break


# Clean up
out.release()
cv2.destroyAllWindows()
