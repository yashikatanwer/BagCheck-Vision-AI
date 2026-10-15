from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time
from collections import deque, Counter
from ultralytics import YOLO

app = Flask(__name__)

model = YOLO("runs/detect/train-4/weights/best.pt")

latest_detections = []

# ---------------------------------------------------------
# TEMPORAL DETECTION SETTINGS
# ---------------------------------------------------------

HISTORY_SIZE = 10
REQUIRED_COUNT = 7

detection_history = deque(maxlen=HISTORY_SIZE)

# ---------------------------------------------------------
# YOLO names → BagCheck names
# ---------------------------------------------------------

YOLO_TO_BAGCHECK = {
    "phone": "Phone",
    "water bottle": "Water Bottle",
    "charger": "Charger",
    "earbuds": "Earbuds",
    "keys": "Keys",
    "lip gloss": "Lip Gloss",
    "notebook": "Notebook",
    "pen": "Pen",
    "sanitizer": "Sanitizer",
    "sunglasses": "Sunglasses",
    "wallet": "Wallet",
    "tiffin": "Tiffin",
    "tissue paper": "Tissue Paper",
    "towel": "Towel"
}

# ---------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------

CLASS_CONFIDENCE = {
    "wallet": 0.65,
    "sunglasses": 0.30
}

DEFAULT_CONFIDENCE = 0.55


@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# CAMERA
# =========================================================

camera = None
camera_thread = None
processing_thread = None

camera_running = False

latest_frame = None
latest_jpeg = None

camera_lock = threading.Lock()
jpeg_lock = threading.Lock()


def camera_loop():

    global camera
    global camera_running
    global latest_frame

    print("Starting camera...")

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():

        print("ERROR: Camera could not be opened.")
        camera_running = False
        return

    print("Camera opened successfully.")

    while camera_running:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")
            time.sleep(0.05)
            continue

        with camera_lock:
            latest_frame = frame.copy()

    camera.release()
    camera = None

    print("Camera stopped.")


# =========================================================
# YOLO PROCESSING
# =========================================================

def processing_loop():

    global latest_frame
    global latest_jpeg
    global latest_detections
    global detection_history

    while camera_running:

        with camera_lock:

            if latest_frame is None:
                frame = None
            else:
                frame = latest_frame.copy()

        if frame is None:

            time.sleep(0.01)
            continue

        # -------------------------------------------------
        # Run YOLO
        # -------------------------------------------------

        results = model(
            frame,
            conf=0.30,
            imgsz=320,
            verbose=False
        )

        current_frame_items = []

        clean_frame = frame.copy()

        # -------------------------------------------------
        # Process detections
        # -------------------------------------------------

        for box in results[0].boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            yolo_name = model.names[class_id].lower()

            if yolo_name not in YOLO_TO_BAGCHECK:
                continue

            bagcheck_name = YOLO_TO_BAGCHECK[yolo_name]

            required_confidence = CLASS_CONFIDENCE.get(
                yolo_name,
                DEFAULT_CONFIDENCE
            )

            if confidence < required_confidence:
                continue

            current_frame_items.append(bagcheck_name)

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            cv2.rectangle(
                clean_frame,
                (x1, y1),
                (x2, y2),
                (255, 105, 180),
                2
            )

            cv2.putText(
                clean_frame,
                f"{bagcheck_name} {confidence:.2f}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 105, 180),
                2
            )

        # -------------------------------------------------
        # Add this frame to history
        # -------------------------------------------------

        detection_history.append(
            set(current_frame_items)
        )

        # -------------------------------------------------
        # Majority-based temporal confirmation
        # -------------------------------------------------

        confirmed_this_frame = []

        if len(detection_history) >= HISTORY_SIZE:

            item_counts = Counter()

            for frame_items in detection_history:

                for item in frame_items:

                    item_counts[item] += 1

            for item, count in item_counts.items():

                if count >= REQUIRED_COUNT:

                    confirmed_this_frame.append(item)

        latest_detections = confirmed_this_frame

        # -------------------------------------------------
        # Encode JPEG
        # -------------------------------------------------

        success, buffer = cv2.imencode(
            ".jpg",
            clean_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80]
        )

        if not success:
            continue

        jpeg_data = buffer.tobytes()

        with jpeg_lock:
            latest_jpeg = jpeg_data

        time.sleep(0.01)


# =========================================================
# START CAMERA
# =========================================================

def start_camera():

    global camera_thread
    global processing_thread
    global camera_running

    if camera_running:
        return

    camera_running = True

    camera_thread = threading.Thread(
        target=camera_loop,
        daemon=True
    )

    processing_thread = threading.Thread(
        target=processing_loop,
        daemon=True
    )

    camera_thread.start()
    processing_thread.start()


# =========================================================
# VIDEO STREAM
# =========================================================

def generate_frames():

    start_camera()

    while camera_running:

        with jpeg_lock:

            if latest_jpeg is None:
                frame_bytes = None
            else:
                frame_bytes = latest_jpeg

        if frame_bytes is None:

            time.sleep(0.01)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            + str(len(frame_bytes)).encode()
            + b"\r\n"
            b"Cache-Control: no-cache, no-store, must-revalidate\r\n"
            b"Pragma: no-cache\r\n"
            b"Expires: 0\r\n"
            b"\r\n"
            + frame_bytes
            + b"\r\n"
        )

        time.sleep(0.01)


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.route("/detections")
def detections():

    return jsonify(latest_detections)


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False,
        threaded=True
    )