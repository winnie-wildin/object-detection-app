# Object Detection App

A microservice architecture for real-time object detection using YOLOv8 and FastAPI.

## Features
Detects objects in images using YOLOv8
Microservice architecture with separate frontend and detection services
Containerized with Docker for easy deployment
RESTful API
Outputs JSON with bounding box coordinates
Saves annotated images and detection data

## Tech Stack

**Frontend Service:**
- FastAPI
- Jinja2 templates
- HTTPX for service communication

**Detection Service:**
- PyTorch (CPU)
- YOLOv8 
- OpenCV

**Infrastructure:**
- Docker & Docker Compose
- Microservices architecture

## Quick Start
```bash
git clone https://github.com/winnie-wildin/object-detection-app.git
cd object-detection-app
docker-compose up --build
```
Then open http://localhost:8000 in your browser and upload an image.

First build takes around 6-10 minutes depending on your internet speed. After that, starting up takes about 30 seconds.

For detailed setup instructions, see [SETUP.md](SETUP.md)

## API Endpoints
**Frontend Service (port 8000):**
- `GET /` - Main web interface
- `GET /health` - Health check

**Detection Service (port 8001):**
- `POST /detect` - Run object detection
- `GET /results/{filename}` - Retrieve result image
- `GET /health` - Health check

## Project Structure
```
object-detection-app/
├── frontend/
│   ├── main.py
│   ├── templates/
│   ├── requirements.txt
│   └── Dockerfile
├── detection-service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── outputs/
├── README.md
└── SETUP.md
```

## Screenshots
**Upload Interface:**

![Upload Interface](screenshots/interface.png)

**Detection Results:**

![Detection Result](screenshots/result.png)

![Annotated Image](screenshots/annotated_image.png)

## Stopping
```bash
docker-compose down
```

## Notes

- CPU-only PyTorch (works on any machine)
- Detection takes ~10-20 seconds per image on CPU
- Model auto-downloads on first run
- Results saved in `outputs/` folder

