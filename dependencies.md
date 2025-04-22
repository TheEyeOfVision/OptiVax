# Compilation Requirements, Operating Environments & Dependencies

## Programming Languages & Runtimes
- **Python** 3.10 or later  
- **Node.js** 16.x LTS or later (for React build)

---

## Backend (Django + REST API)

### Frameworks & Libraries
- **Django** 5.1.6  
- **Django REST Framework** 3.15.2  

### Data‑Science & Algorithm Libraries
- **NumPy** 2.2.2  
- **Pandas** 2.2.3  
- **OSMnx** 2.0.1  
- **NetworkX** 3.4.2  
- **geneticalgorithm** 1.0.2  

### System Prerequisites
- GDAL/GEOS system libraries (for OSMnx):
  ```bash
  # Ubuntu / Debian
  sudo apt update && \
  sudo apt install -y gdal-bin libgdal-dev libgeos-dev
  ```  

### Install Backend Dependencies
```bash
pip install \
  Django==5.1.6 \
  djangorestframework==3.15.2 \
  numpy==2.2.2 \
  pandas==2.2.3 \
  osmnx==2.0.1 \
  networkx==3.4.2 \
  geneticalgorithm==1.0.2
```

---

## Frontend (React + Leaflet)

### Core UI & State
- **react** ^19.0.0  
- **react-dom** ^19.0.0  
- **react-scripts** ^5.0.1  

### Mapping & Geospatial Tools
- **leaflet** ^1.7.1  
- **react‑leaflet** ^3.2.0  
- **react‑leaflet‑draw** ^0.19.8  
- **react‑leaflet‑markercluster** ^3.0.0‑rc1  
- **leaflet‑draw** ^1.0.4  
- **leaflet‑fullscreen** ^1.0.2  
- **@turf/turf** ^6.4.0  

### UI Libraries & Styling
- **@mui/material** ^5.16.7  
- **@mui/icons-material** ^7.0.0  
- **@emotion/react** ^11.13.0  
- **@emotion/styled** ^11.13.0  
- **sass** ^1.35.1  

### Networking & Utilities
- **axios** ^1.7.3  
- **react‑router‑dom** ^5.2.0  
- **react‑icons** ^5.5.0  
- **react‑tabs** ^3.2.3  
- **gh‑pages** ^3.2.3  
- **web‑vitals** ^1.0.1  
- **webpack** ^5.95.0  

### Testing
- **@testing-library/react** ^11.1.0  
- **@testing-library/jest-dom** ^5.11.4  
- **@testing-library/user-event** ^12.1.10  

### Install Frontend Dependencies
```bash
npm install
# —or pin exact versions—
npm install \
  react@19.0.0 react-dom@19.0.0 react-scripts@5.0.1 \
  leaflet@1.7.1 react-leaflet@3.2.0 react-leaflet-draw@0.19.8 \
  react-leaflet-markercluster@3.0.0-rc1 leaflet-draw@1.0.4 leaflet-fullscreen@1.0.2 \
  @turf/turf@6.4.0 \
  @mui/material@5.16.7 @mui/icons-material@7.0.0 \
  @emotion/react@11.13.0 @emotion/styled@11.13.0 \
  sass@1.35.1 axios@1.7.3 react-router-dom@5.2.0 \
  react-icons@5.5.0 react-tabs@3.2.3 gh-pages@3.2.3 \
  web-vitals@1.0.1 webpack@5.95.0 \
  @testing-library/react@11.1.0 @testing-library/jest-dom@5.11.4 \
  @testing-library/user-event@12.1.10
```

---

## Operating Systems Tested
- Ubuntu 20.04+ / Debian‑based Linux  
- Windows 10+ / macOS Monterey+

---

## Build & Deploy

### Backend (Docker)
```bash
docker build -t my-django-app .
docker run -p 8000:8000 my-django-app
```

### Frontend
```bash
npm run build
npm run deploy   # publishes to GH Pages
```
