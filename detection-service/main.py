from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import torch
import cv2
import numpy as np
from pathlib import Path
import os
import json
from datetime import datetime
from ultralytics import YOLO

app = FastAPI(title="Object Detection Service")

# Setup directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Load YOLOv8 model 
print("Loading YOLOv8 model..")
model = YOLO('yolov8s.pt')  
model.conf = 0.15
model.iou = 0.45
print("Model has loaded successfully!")

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_path = f"uploads/{timestamp}_{file.filename}"
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Try detection with lower thresholds
        thresholds = [0.25, 0.15, 0.10, 0.05]
        detections = []
        used_threshold = None
        
        for threshold in thresholds:
            model.conf = threshold
            results = model(upload_path)[0]
            
            temp_detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                temp_detections.append({
                    "class": results.names[cls],
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })
            
            if temp_detections:
                detections = temp_detections
                used_threshold = threshold
                print(f"Found {len(detections)} objects with threshold {threshold}")
                break
            else:
                print(f"No detections with threshold {threshold}, trying lower ...")
        
        # Save result image with bounding boxes
        result_path = f"results/{timestamp}_{file.filename}"
        
        if detections:
            # Draw bounding boxes
            img = cv2.imread(upload_path)
            for det in detections:
                x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
                label = f"{det['class']} {det['confidence']:.2f}"
                
                cv2.rectangle(img, (x1, y1), (x2, y2), (44, 36, 32), 2)
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(img, (x1, y1 - label_h - 10), (x1 + label_w, y1), (44, 36, 32), -1)
                cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 241, 232), 2)
            
            cv2.imwrite(result_path, img)
            
            # Save JSON results
            json_path = f"results/{timestamp}_{Path(file.filename).stem}.json"
            with open(json_path, "w") as f:
                json.dump(detections, f, indent=2)
            
            return JSONResponse({
                "success": True,
                "detections": detections,
                "result_image": f"{timestamp}_{file.filename}",
                "total_objects": len(detections),
                "threshold_used": used_threshold,
                "message": f"Detected {len(detections)} object(s) with confidence threshold {used_threshold}"
            })
        else:
            # No detections even with lowest threshold - copy original image
            img = cv2.imread(upload_path)
            cv2.imwrite(result_path, img)
            
            return JSONResponse({
                "success": True,
                "detections": [],
                "result_image": f"{timestamp}_{file.filename}",
                "total_objects": 0,
                "threshold_used": 0.05,
                "message": "Couldn't detect anything even with relaxed thresholds but COCO's still clueless.",
                "no_detections": True
            })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
    
@app.get("/results/{filename}")
async def get_result(filename: str):
    file_path = f"results/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "detection-service",
        "model": "yolov8s",
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)