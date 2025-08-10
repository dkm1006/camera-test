import cv2
from picamera2 import Picamera2
import time

 
def init_video_capture():
    """Initialize video capture"""
    pc = Picamera2()
    pc.configure(pc.create_preview_configuration(
        main={
            # "format": "YUV420",  # this gives an image in gray with multiple smaller versions underneath, shape 720, 640
            "format": "XRGB8888",
            "size": (640, 480)
        })
    )
    pc.start()
    return pc


def init_video_writer():
    """Video writer initialization with explicit FPS"""
    save_fps = 15.0  # Adjust this based on your actual processing speed
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("output.mp4", fourcc, save_fps, (640, 480))
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
out = init_video_writer()
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# Current mode
mode = "normal"
# FPS calculation
prev_time = time.time()

while True:
    display_frame = get_frame(capture)
    if mode == "red":
        display_frame = cv2.cvtColor(display_frame[:,:,0], cv2.COLOR_GRAY2BGR)
    elif mode == "green":
        display_frame = cv2.cvtColor(display_frame[:,:,1], cv2.COLOR_GRAY2BGR)
 
    elif mode == "blue":
        display_frame = cv2.cvtColor(display_frame[:,:,2], cv2.COLOR_GRAY2BGR)
 
    elif mode == "infrared":
        display_frame = cv2.cvtColor(display_frame[:,:,3], cv2.COLOR_GRAY2BGR)
 
    
    elif mode == "threshold":
        gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
        _, display_frame = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
 
    elif mode == "edge":
        gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        display_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
 
    elif mode == "bg_sub":
        fg_mask = bg_subtractor.apply(display_frame)
        display_frame = cv2.bitwise_and(display_frame, display_frame, mask=fg_mask)
 
    elif mode == "contour":
        gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        display_frame = cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 2)
 
    # Calculate actual processing FPS
    curr_time = time.time()
    processing_fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
 
    # Display actual processing FPS
    cv2.putText(
        display_frame, f"FPS: {int(processing_fps)} Mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )
 
    # Write frame to video
    out.write(display_frame)
 
    # Show video
    cv2.imshow("Live Video", display_frame)

    mode = obtain_user_command(mode)
    if mode == "quit":
        break


# Clean up
out.release()
cv2.destroyAllWindows()
