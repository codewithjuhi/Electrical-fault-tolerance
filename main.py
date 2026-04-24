from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
import pickle
import os

app = FastAPI(title="Electrical Fault Detection & Classification API")

# Add CORS middleware to allow Streamlit to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models
detection_model = None
classification_model = None
models_loaded = False

class FaultInput(BaseModel):
    Ia: float
    Ib: float
    Ic: float
    Va: float
    Vb: float
    Vc: float

class FaultDetectionResponse(BaseModel):
    fault_detected: bool
    probability: float

class FaultClassificationResponse(BaseModel):
    ground: bool
    phase_a: bool
    phase_b: bool
    phase_c: bool
    fault_type: str

def load_models():
    """Load or train the models"""
    global detection_model, classification_model, models_loaded
    
    try:
        # Load pre-trained models if available
        if os.path.exists('detection_model.pkl') and os.path.exists('classification_model.pkl'):
            with open('detection_model.pkl', 'rb') as f:
                detection_model = pickle.load(f)
            with open('classification_model.pkl', 'rb') as f:
                classification_model = pickle.load(f)
            print("Models loaded from saved files")
        else:
            # Train models from dataset
            print("Training models from dataset...")
            
            # Load data
            detection_train = pd.read_excel('detect_dataset.xlsx').dropna(axis=1)
            class_train = pd.read_csv('classData.csv').dropna(axis=1)
            
            features = ['Ia', 'Ib', 'Ic', 'Va', 'Vb', 'Vc']
            class_target = ['G', 'C', 'B', 'A']
            
            # Prepare data
            detection_data_X = detection_train[features]
            class_data_X = class_train[features]
            detection_data_Y = detection_train['Output (S)']
            class_data_Y = class_train[class_target]
            
            # Split data
            detection_train_X, _, detection_train_Y, _ = train_test_split(
                detection_data_X, detection_data_Y, test_size=0.33, random_state=1
            )
            class_train_X, _, class_train_Y, _ = train_test_split(
                class_data_X, class_data_Y, test_size=0.33, random_state=1
            )
            
            # Train Detection Model (Decision Tree)
            detection_model = DecisionTreeClassifier(random_state=42)
            detection_model.fit(detection_train_X, detection_train_Y)
            
            # Train Classification Model (Multi-output Decision Tree)
            classification_model = MultiOutputClassifier(
                DecisionTreeClassifier(random_state=42)
            )
            classification_model.fit(class_train_X, class_train_Y)
            
            # Save models
            with open('detection_model.pkl', 'wb') as f:
                pickle.dump(detection_model, f)
            with open('classification_model.pkl', 'wb') as f:
                pickle.dump(classification_model, f)
            print("Models trained and saved")
        
        models_loaded = True
    except Exception as e:
        print(f"Error loading models: {e}")
        models_loaded = False

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    load_models()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Electrical Fault Detection & Classification API",
        "endpoints": {
            "detect": "/detect",
            "classify": "/classify",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "models_loaded": models_loaded
    }

@app.post("/detect", response_model=FaultDetectionResponse)
async def detect_fault(input_data: FaultInput):
    """
    Detect if a fault is present in the electrical system
    
    Input:
    - Ia, Ib, Ic: Phase currents
    - Va, Vb, Vc: Phase voltages
    
    Output:
    - fault_detected: Boolean indicating if fault is detected
    - probability: Confidence score (0-1)
    """
    if not models_loaded:
        return {"error": "Models not loaded"}
    
    try:
        # Prepare input
        X = np.array([[input_data.Ia, input_data.Ib, input_data.Ic, 
                      input_data.Va, input_data.Vb, input_data.Vc]])
        
        # Predict
        prediction = detection_model.predict(X)[0]
        
        # Get probability if available
        try:
            probabilities = detection_model.predict_proba(X)[0]
            probability = float(max(probabilities))
        except:
            probability = float(prediction)
        
        fault_detected = bool(prediction == 1)
        
        return {
            "fault_detected": fault_detected,
            "probability": probability
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/classify", response_model=FaultClassificationResponse)
async def classify_fault(input_data: FaultInput):
    """
    Classify the type of fault in the electrical system
    
    Input:
    - Ia, Ib, Ic: Phase currents
    - Va, Vb, Vc: Phase voltages
    
    Output:
    - ground, phase_a, phase_b, phase_c: Boolean indicators for each fault type
    - fault_type: Human-readable fault type description
    """
    if not models_loaded:
        return {"error": "Models not loaded"}
    
    try:
        # Prepare input
        X = np.array([[input_data.Ia, input_data.Ib, input_data.Ic, 
                      input_data.Va, input_data.Vb, input_data.Vc]])
        
        # Predict
        prediction = classification_model.predict(X)[0]
        
        # Decode prediction in order [G, C, B, A]
        ground = bool(prediction[0])
        phase_c = bool(prediction[1])
        phase_b = bool(prediction[2])
        phase_a = bool(prediction[3])
        
        # Determine a simple fault type label
        if prediction.tolist() == [0, 0, 0, 0]:
            fault_type = "No Fault"
        elif prediction.tolist() == [1, 0, 0, 1]:
            fault_type = "LG Fault"
        elif prediction.tolist() == [0, 0, 1, 1]:
            fault_type = "LL Fault"
        elif prediction.tolist() == [1, 0, 1, 1]:
            fault_type = "LLG Fault"
        elif prediction.tolist() == [0, 1, 1, 1]:
            fault_type = "LLL Fault"
        elif prediction.tolist() == [1, 1, 1, 1]:
            fault_type = "LLLG Fault"
        else:
            fault_type = "Unknown Fault"
        
        return {
            "ground": ground,
            "phase_a": phase_a,
            "phase_b": phase_b,
            "phase_c": phase_c,
            "fault_type": fault_type
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
