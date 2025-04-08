from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from pose_analysis import analyze_pose
import threading

app = Flask(__name__)

# Performance optimization flags
USE_JPEG_COMPRESSION = True
RESIZE_FRAME = True
TARGET_FPS = 24

# Global variables with thread safety
camera = None
feedback = "Initializing..."
frame_lock = threading.Lock()
latest_frame = None
latest_processed_frame = None
latest_feedback = "Waiting for pose detection..."

def camera_thread():
    global camera, latest_frame, latest_processed_frame, latest_feedback
    
    # Initialize camera with optimized settings
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reduce buffer size
    
    while True:
        ret, frame = camera.read()
        if not ret:
            break
            
        if RESIZE_FRAME:
            frame = cv2.resize(frame, (320, 240))
            
        # Process frame
        processed_frame, current_feedback = analyze_pose(frame)
        
        with frame_lock:
            latest_frame = frame
            latest_processed_frame = processed_frame
            latest_feedback = current_feedback

def generate_frames():
    while True:
        with frame_lock:
            if latest_processed_frame is None:
                continue
                
            frame = latest_processed_frame
            
            if USE_JPEG_COMPRESSION:
                ret, buffer = cv2.imencode('.jpg', frame, [
                    cv2.IMWRITE_JPEG_QUALITY, 60,
                    cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1
                ])
                frame = buffer.tobytes()
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_feedback')
def get_feedback():
    with frame_lock:
        return jsonify({"feedback": latest_feedback})

if __name__ == '__main__':
    # Start camera thread
    threading.Thread(target=camera_thread, daemon=True).start()
    
    # Run Flask app with optimized settings
    app.run(
        debug=False,  # Disable debug mode for production
        threaded=True,
        processes=1,
        host='0.0.0.0',
        port=5000
    )