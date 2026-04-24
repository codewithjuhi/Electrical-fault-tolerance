# Quick Start Guide

## What Was Created

✅ **FastAPI Backend** (`main.py`)
- REST API for fault detection and classification
- Automatic model training/loading
- 3 main endpoints: `/detect`, `/classify`, `/health`
- Swagger documentation at `http://localhost:8000/docs`

✅ **Streamlit Frontend** (`app.py`)
- Interactive web interface with 5 pages:
  - Home: System overview and metrics
  - Fault Detection: Real-time detection with sliders
  - Fault Classification: Classify fault types
  - Batch Analysis: Process multiple samples
  - Documentation: API reference

✅ **Dependencies** (`requirements.txt`)
- All required packages listed

✅ **Deployment Scripts**
- `run_all.bat` (Windows)
- `run_all.sh` (Linux/Mac)

✅ **Documentation** (`DEPLOYMENT_GUIDE.md`)
- Complete setup and deployment instructions

---

## Getting Started (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Everything (Windows)
```bash
run_all.bat
```

Or (Linux/Mac):
```bash
bash run_all.sh
```

### Step 3: Open in Browser
- **Streamlit App**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

---

## Or Run Separately (for development)

**Terminal 1 - FastAPI:**
```bash
python main.py
```

**Terminal 2 - Streamlit:**
```bash
streamlit run app.py
```

---

## Features

### 🔍 Fault Detection
- Real-time detection of electrical faults
- Confidence scoring
- Interactive input controls

### 📊 Fault Classification
- Identify specific fault types:
  - Line-to-Ground (LG)
  - Line-to-Line (LL)
  - Line-to-Line-to-Ground (LLG)
  - Three-Phase (LLL/LLLG)

### 📈 Batch Analysis
- Upload CSV files with multiple samples
- Process in bulk
- View detection statistics

### 📚 API Documentation
- Full Swagger/OpenAPI docs
- Interactive endpoint testing
- Example requests/responses

---

## Model Performance

| Metric | Detection | Classification |
|--------|-----------|-----------------|
| Accuracy | 99.47% | 99.38% |
| Error Rate | 0.53% | 0.62% |
| Model | Decision Tree | Polynomial Regression |
| Processing Time | <100ms | <100ms |

---

## Troubleshooting

**"API Connection Error"**
- Ensure both FastAPI (port 8000) and Streamlit (port 8501) are running
- Check Windows Firewall settings

**"Models not loading"**
- Verify `classData.csv` and `detect_dataset.xlsx` exist
- Try deleting `.pkl` files to retrain

**"Port already in use"**
- Change ports in code or close existing services:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

---

## Next Steps

1. ✅ Run the application
2. 📊 Test detection/classification in Streamlit UI
3. 📁 Try batch analysis with CSV files
4. 🚀 Deploy to cloud (Streamlit Cloud, Docker, AWS, Azure)
5. 🔄 Retrain with new data as needed

---

## Deployment Options

- **Local**: Run startup script
- **Docker**: Build and run container
- **Streamlit Cloud**: Connect GitHub repo
- **AWS/Azure**: Deploy with serverless functions

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

**Ready to go!** 🚀
