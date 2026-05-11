## Resq – AI Based Disaster Relief and Management System

This project implements **Resq (Disaster Relief and Management System)**, an AI‑powered decision support system for managing natural and man‑made disasters across three phases:

- **Pre‑disaster**: early detection and risk prediction
- **During disaster**: real‑time alerting and rescue coordination
- **Post‑disaster**: relief distribution and recovery planning

### High‑Level Modules

- **City‑Fire Detector**
  - CNN/VGG‑based model (`fire.model`) that detects fire from CCTV or drone video streams.
- **Flood Detector**
  - CNN/VGG‑based model (`flood.model`) that detects flood water and inundation levels from video.
- **Social‑Distance Detector**
  - YOLOv3‑based human detection + distance estimation for crowding and social‑distancing violations.
- **Risk Clustering (DBSCAN)**
  - Groups incident locations into high‑distress clusters.
- **Routing & Resource Allocation (GRASP + VND)**
  - Computes near‑optimal rescue and relief routes.
- **Web Backend (Django)**
  - REST APIs and admin dashboard to orchestrate the above modules.

### Repository Layout

- `backend/` – Django project and REST APIs.
- `detectors/` – Fire, flood, and social‑distance detection modules (to be wired with your trained models).
- `routing_optimization/` – DBSCAN clustering and GRASP/VND routing utilities.
- `videos/` – Sample input videos for demo.
- `docs/` – Project reports, diagrams, and supporting documentation.

### Quick Start

1. **Create and activate a virtual environment (recommended)**  
   On Windows (PowerShell):

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations and run the backend**:

   ```bash
   cd backend
   python manage.py migrate
   python manage.py runserver
   ```

4. Open the browser at `http://127.0.0.1:8000/` to access the Resq backend.

### Model Files (Not Stored in Git)

Download the pre‑trained models from your Drive link and place them as follows:

- `detectors/city_fire/output/fire.model`
- `detectors/flood/output/flood.model`
- `detectors/social_distance/yolo-coco/yolov3.weights`

These paths will be used by the detector modules.

### Next Steps

- Implement the actual model loading and prediction logic inside the detector modules.
- Connect real GIS/location data to DBSCAN clustering.
- Integrate a frontend (Django templates or SPA) with live maps and dashboards.

