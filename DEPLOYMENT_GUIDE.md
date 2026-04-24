# FastAPI + Streamlit Deployment Guide

## Project Structure

```
Electrical-Fault-detection-and-classification/
├── main.py                          # FastAPI backend
├── app.py                           # Streamlit frontend
├── requirements.txt                 # Python dependencies
├── run_all.sh / run_all.bat         # Startup script
├── fault detection and classification.ipynb   # Original notebook
├── fault detection and classification.py      # Original script
├── classData.csv                    # Classification dataset
├── detect_dataset.xlsx              # Detection dataset
└── README.md                        # Original documentation
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Data Files

Make sure these files exist in the project directory:
- `classData.csv`
- `detect_dataset.xlsx`

## Running the Application

### Option 1: Run Everything at Once

**Windows:**
```bash
run_all.bat
```

**Linux/Mac:**
```bash
bash run_all.sh
```

### Option 2: Run Separately

**Terminal 1 - Start FastAPI Backend:**
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

**Terminal 2 - Start Streamlit Frontend:**
```bash
streamlit run app.py
```

The Streamlit app will be available at: `http://localhost:8501`

## API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "models_loaded": true
}
```

### Detect Fault
```
POST http://localhost:8000/detect
Content-Type: application/json

{
  "Ia": 50.0,
  "Ib": -25.0,
  "Ic": -25.0,
  "Va": 230.0,
  "Vb": -115.0,
  "Vc": -115.0
}
```

Response:
```json
{
  "fault_detected": false,
  "probability": 0.95
}
```

### Classify Fault
```
POST http://localhost:8000/classify
Content-Type: application/json

{
  "Ia": 50.0,
  "Ib": -25.0,
  "Ic": -25.0,
  "Va": 230.0,
  "Vb": -115.0,
  "Vc": -115.0
}
```

Response:
```json
{
  "ground": false,
  "phase_a": false,
  "phase_b": false,
  "phase_c": false,
  "fault_type": "No Fault"
}
```

## Using Streamlit Web Interface

The Streamlit interface includes:

1. **Home** - Overview and system statistics
2. **Fault Detection** - Real-time fault detection with interactive sliders
3. **Fault Classification** - Classify specific fault types
4. **Batch Analysis** - Upload CSV files and analyze multiple samples
5. **Documentation** - System documentation and API reference

### Batch Analysis

To use batch analysis, prepare a CSV file with columns:
```
Ia,Ib,Ic,Va,Vb,Vc
50.0,-25.0,-25.0,230.0,-115.0,-115.0
45.0,-22.5,-22.5,225.0,-112.5,-112.5
...
```

## Troubleshooting

### API Connection Error
- Ensure FastAPI backend is running on port 8000
- Check firewall settings
- Verify CORS is enabled

### Models Not Loading
- Verify `classData.csv` and `detect_dataset.xlsx` exist
- Check file permissions
- Ensure scikit-learn is properly installed

### Streamlit Issues
- Clear cache: `streamlit cache clear`
- Restart Streamlit server
- Check port availability (default: 8501)

## Deployment Options

### Local Development
```bash
python main.py &
streamlit run app.py
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python main.py & streamlit run app.py"]
```

Build and run:
```bash
docker build -t fault-detection-app .
docker run -p 8000:8000 -p 8501:8501 fault-detection-app
```

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repository
4. Deploy

Note: For Streamlit Cloud, you'll need to deploy FastAPI separately (e.g., on Heroku, AWS, or Azure)

## Performance Notes

- Detection model: Decision Tree (fast, <100ms per prediction)
- Classification model: Polynomial Regression (fast, <100ms per prediction)
- Batch processing: ~10,000 samples per minute on standard hardware

## Model Retraining

To retrain models on new data:

1. Replace or update `classData.csv` and `detect_dataset.xlsx`
2. Delete the saved model files:
   ```bash
   rm detection_model.pkl classification_model.pkl
   ```
3. Restart the FastAPI backend to retrain models

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
