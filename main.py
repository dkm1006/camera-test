import time

import cv2
from picamera2 import Picamera2

from storage import store_crossing


DEST_IP = '0.0.0.0'
DEST_PORT = '8554'



def main():
    capture = init_video_capture()
    prev_time = time.time()
    while True:
        try:
            # Calculate actual processing FPS
            curr_time = time.time()
            processing_fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            frame = capture_frame(capture)
            # TODO: Finish main loop
            # Detect objects
            # Calculate centroids
            # Track objects
            # Store crossings
            # Draw object bounding boxes and centroids
            # Stream frames

        except Exception as e:
            print(e)
            break

    # Clean up
    capture.stop_recording()
    cv2.destroyAllWindows()



def main(transform=lambda f: f, **kwargs):
    capture = init_video_capture()
    # FPS calculation
    prev_time = time.time()
    while True:
        try:
            # Calculate actual processing FPS
            curr_time = time.time()
            processing_fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            frame = transform(capture_frame(capture), fps=processing_fps, **kwargs)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(e)
            break

    # Clean up
    capture.stop_recording()
    cv2.destroyAllWindows()


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


def capture_frame(capture):
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


def test(frame, mode='normal', fps=30):
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
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

    # Display actual processing FPS
    cv2.putText(
        frame, f"FPS: {int(fps)} Mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )

    # Write frame to video
    # out.write(frame)

    # Show video
    # cv2.imshow("Live Video", frame)

    # Clean up
    # out.release()
    # cv2.destroyAllWindows()



if __name__ == '__main__':
    main()