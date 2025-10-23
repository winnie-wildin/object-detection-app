# Setup Guide

## Installation Steps

### Step 1: Install Docker Desktop

### Step 2: Download the Project

Clone the repository:
```bash
git clone https://github.com/winnie-wildin/object-detection-app.git
cd object-detection-app
```

### Step 3: Build and Run

In the project directory, run:
```bash
docker-compose up --build
```

**First build takes ~6-10 minutes** depending on your internet speed (tested at 25 Mbps: ~8 minutes). 

Wait until you see:
```
frontend           | INFO:     Application startup complete.
detection-service  | INFO:     Application startup complete.
```

### Step 4: Access the App

Open browser: http://localhost:8000

Upload an image and click detect. Results save to the `outputs/` folder.

## Stopping the App

Press `Ctrl+C` in the terminal, then run:
```bash
docker-compose down
```

## Restarting the App

After stopping, simply run:
```bash
docker-compose up
```

## Viewing Logs
```bash
docker-compose logs -f
```

## Complete Cleanup

Remove everything (containers + images):
```bash
docker-compose down -v --rmi all
```