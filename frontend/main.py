from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
import json
from pathlib import Path

app = FastAPI(title="Object Detection Frontend")
templates = Jinja2Templates(directory="templates")

os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/results", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
DETECTION_SERVICE_URL = os.getenv("DETECTION_SERVICE_URL", "http://detection-service:8001")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
   
        file_path = f"static/uploads/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Send to detection service
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": (file.filename, f, file.content_type)}
                response = await client.post(
                    f"{DETECTION_SERVICE_URL}/detect",
                    files=files
                )
        
        if response.status_code == 200:
            result = response.json()
            
            # Save result image and JSON
            result_image_path = f"static/results/{file.filename}"
            json_path = f"static/results/{Path(file.filename).stem}.json"
            
            # Download detected image 
            async with httpx.AsyncClient() as client:
                img_response = await client.get(
                    f"{DETECTION_SERVICE_URL}/results/{result['result_image']}"
                )
                with open(result_image_path, "wb") as f:
                    f.write(img_response.content)
            
            # Save JSON
            with open(json_path, "w") as f:
                json.dump(result["detections"], f, indent=2)
            
            return JSONResponse({
                "success": True,
                "original_image": f"/static/uploads/{file.filename}",
                "result_image": f"/static/results/{file.filename}",
                "detections": result["detections"],
                "json_file": f"/static/results/{Path(file.filename).stem}.json",
                "total_objects": result["total_objects"],
                "threshold_used": result.get("threshold_used"),
                "message": result["message"],
                "no_detections": result.get("no_detections", False)
            })
        else:
            return JSONResponse({
                "success": False,
                "error": f"Detection service returned {response.status_code}"
            }, status_code=500)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
    
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "frontend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)