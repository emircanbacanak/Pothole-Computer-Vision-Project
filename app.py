from flask import Flask, render_template, Response, jsonify
import cv2
import supervision as sv
from ultralytics import YOLO
import time
import threading

app = Flask(__name__)

# PyResearch Configuration
PR_MODEL_PATH = "best.pt"
detection_count = 0
fps_counter = 0
last_fps_update = time.time()

class VideoProcessor:
    def __init__(self):
        self.model = YOLO(PR_MODEL_PATH)
        self.box_annotator = sv.BoundingBoxAnnotator(
            thickness=2,
            color=sv.Color.from_hex("#0055FF")
        )
        self.label_annotator = sv.LabelAnnotator(
            text_scale=0.7,
            text_thickness=1,
            text_color=sv.Color.WHITE
        )
        self.frame_buffer = []
        self.lock = threading.Lock()
        self.running = True

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        frame_skip = 1
        frame_count = 0
        
        while self.running and cap.isOpened():
            start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % (frame_skip + 1) != 0:
                continue
                
            # Model inference
            results = self.model(frame)[0]
            detections = sv.Detections.from_ultralytics(results)
            
            # Update global detection count
            global detection_count
            detection_count = len(detections)
            
            # Annotation
            annotated_frame = self.box_annotator.annotate(frame.copy(), detections)
            annotated_frame = self.label_annotator.annotate(annotated_frame, detections)
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            with self.lock:
                if len(self.frame_buffer) < 5:
                    self.frame_buffer.append(buffer.tobytes())
            
            # FPS kontrolü
            elapsed = time.time() - start_time
            target_delay = 1.0 / 60.0
            if elapsed < target_delay:
                time.sleep(target_delay - elapsed)
                
        cap.release()

def generate_frames():
    processor = VideoProcessor()
    video_thread = threading.Thread(target=processor.process_video, args=("demo.mp4",))
    video_thread.daemon = True
    video_thread.start()
    
    try:
        while True:
            with processor.lock:
                if processor.frame_buffer:
                    frame = processor.frame_buffer.pop(0)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    time.sleep(0.001)
                    
            # FPS hesaplama
            global fps_counter, last_fps_update
            fps_counter += 1
            if time.time() - last_fps_update >= 1.0:
                last_fps_update = time.time()
                fps_counter = 0
                
    finally:
        processor.running = False
        video_thread.join()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_data')
def detection_data():
    global detection_count, fps_counter
    return jsonify({
        'detections': detection_count,
        'fps': fps_counter,
        'new_detections': []
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')