import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://localhost:8001"

st.set_page_config(
    page_title="Electrical Fault Detection System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("⚡ Electrical Fault Detection & Classification System")
with col2:
    st.markdown("### API Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Error")
    except:
        st.error("🔴 API Offline")

st.markdown("---")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", 
    ["Home", "Fault Detection", "Fault Classification", "Batch Analysis", "Documentation"])

# HOME PAGE
if page == "Home":
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Welcome to the Fault Detection System")
        st.write("""
        This application uses Artificial Neural Networks (ANNs) to detect and classify 
        electrical faults in power transmission systems.
        
        **Key Features:**
        - Real-time fault detection
        - Fault type classification
        - Batch analysis capability
        - High accuracy (>99%)
        
        **Faults Detected:**
        - Line to Ground (LG)
        - Line to Line (LL)
        - Double Line to Ground (LLG)
        - Three Phase Symmetrical (LLLG)
        """)
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=Power+System", 
                caption="Power Transmission System", use_column_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detection Accuracy", "99.47%", "+0.53%")
    with col2:
        st.metric("Classification Accuracy", "99.38%", "+0.62%")
    with col3:
        st.metric("Processing Time", "<100ms", "Per sample")

# FAULT DETECTION PAGE
elif page == "Fault Detection":
    st.header("🔍 Fault Detection")
    st.write("Determine if a fault is present in the electrical system")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Measurements")
        
        # Input sliders for Phase Currents
        st.write("**Phase Currents (A):**")
        ia = st.slider("Phase A Current (Ia)", -200.0, 200.0, 50.0, key="ia_detect")
        ib = st.slider("Phase B Current (Ib)", -200.0, 200.0, -25.0, key="ib_detect")
        ic = st.slider("Phase C Current (Ic)", -200.0, 200.0, -25.0, key="ic_detect")
        
        # Input sliders for Phase Voltages
        st.write("**Phase Voltages (V):**")
        va = st.slider("Phase A Voltage (Va)", -400.0, 400.0, 230.0, key="va_detect")
        vb = st.slider("Phase B Voltage (Vb)", -400.0, 400.0, -115.0, key="vb_detect")
        vc = st.slider("Phase C Voltage (Vc)", -400.0, 400.0, -115.0, key="vc_detect")
        
        if st.button("🔍 Analyze for Faults", key="detect_button", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/detect",
                        json={
                            "Ia": ia, "Ib": ib, "Ic": ic,
                            "Va": va, "Vb": vb, "Vc": vc
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.detection_result = result
                    else:
                        st.error("Error from API")
                except Exception as e:
                    st.error(f"Connection error: {e}")
    
    with col2:
        st.subheader("Results")
        
        if "detection_result" in st.session_state:
            result = st.session_state.detection_result
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                # Display results
                if result['fault_detected']:
                    st.error("⚠️ **FAULT DETECTED**", icon="⚠️")
                else:
                    st.success("✅ **NO FAULT DETECTED**", icon="✅")
                
                # Confidence gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=result['probability'] * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confidence Level (%)"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 80], 'color': "lightyellow"},
                               {'range': [80, 100], 'color': "lightgreen"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 90}}
                ))
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Detection Status", 
                             "FAULT" if result['fault_detected'] else "NORMAL")
                with col2:
                    st.metric("Confidence", f"{result['probability']*100:.2f}%")

# FAULT CLASSIFICATION PAGE
elif page == "Fault Classification":
    st.header("📊 Fault Classification")
    st.write("Identify the specific type of electrical fault")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Measurements")
        
        st.write("**Phase Currents (A):**")
        ia = st.slider("Phase A Current (Ia)", -200.0, 200.0, 50.0, key="ia_class")
        ib = st.slider("Phase B Current (Ib)", -200.0, 200.0, -25.0, key="ib_class")
        ic = st.slider("Phase C Current (Ic)", -200.0, 200.0, -25.0, key="ic_class")
        
        st.write("**Phase Voltages (V):**")
        va = st.slider("Phase A Voltage (Va)", -400.0, 400.0, 230.0, key="va_class")
        vb = st.slider("Phase B Voltage (Vb)", -400.0, 400.0, -115.0, key="vb_class")
        vc = st.slider("Phase C Voltage (Vc)", -400.0, 400.0, -115.0, key="vc_class")
        
        if st.button("📊 Classify Fault", key="classify_button", use_container_width=True):
            with st.spinner("Classifying..."):
                try:
                    response = requests.post(
                        f"{API_URL}/classify",
                        json={
                            "Ia": ia, "Ib": ib, "Ic": ic,
                            "Va": va, "Vb": vb, "Vc": vc
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.classification_result = result
                    else:
                        st.error("Error from API")
                except Exception as e:
                    st.error(f"Connection error: {e}")
    
    with col2:
        st.subheader("Fault Classification Results")
        
        if "classification_result" in st.session_state:
            result = st.session_state.classification_result
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.info(f"🔹 **Fault Type: {result['fault_type']}**")
                
                # Display fault components
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Ground Fault", "YES" if result['ground'] else "NO")
                    st.metric("Phase A Involved", "YES" if result['phase_a'] else "NO")
                with col2:
                    st.metric("Phase B Involved", "YES" if result['phase_b'] else "NO")
                    st.metric("Phase C Involved", "YES" if result['phase_c'] else "NO")
                
                # Fault components visualization
                fault_components = {
                    'Ground': result['ground'],
                    'Phase A': result['phase_a'],
                    'Phase B': result['phase_b'],
                    'Phase C': result['phase_c']
                }
                
                colors = ['green' if v else 'lightgray' for v in fault_components.values()]
                fig = px.bar(x=list(fault_components.keys()), 
                           y=[1]*4, 
                           color=colors,
                           title="Fault Components",
                           height=300)
                fig.update_yaxes(showticklabels=False)
                st.plotly_chart(fig, use_container_width=True)

# BATCH ANALYSIS PAGE
elif page == "Batch Analysis":
    st.header("📈 Batch Analysis")
    st.write("Analyze multiple samples at once")
    
    uploaded_file = st.file_uploader("Upload CSV file with fault measurements", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.subheader("Preview Data")
            st.dataframe(df.head())
            
            if st.button("🔄 Analyze All Samples"):
                with st.spinner("Processing batch..."):
                    results = []
                    
                    for idx, row in df.iterrows():
                        try:
                            response = requests.post(
                                f"{API_URL}/detect",
                                json={
                                    "Ia": row['Ia'],
                                    "Ib": row['Ib'],
                                    "Ic": row['Ic'],
                                    "Va": row['Va'],
                                    "Vb": row['Vb'],
                                    "Vc": row['Vc']
                                }
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                results.append({
                                    'Sample': idx + 1,
                                    'Fault Detected': result.get('fault_detected', False),
                                    'Confidence': result.get('probability', 0)
                                })
                        except:
                            pass
                    
                    results_df = pd.DataFrame(results)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Samples", len(results_df))
                    with col2:
                        faults = results_df['Fault Detected'].sum()
                        st.metric("Faults Detected", faults)
                    with col3:
                        st.metric("Detection Rate", f"{(faults/len(results_df)*100):.1f}%")
                    
                    st.dataframe(results_df)
        except Exception as e:
            st.error(f"Error processing file: {e}")

# DOCUMENTATION PAGE
elif page == "Documentation":
    st.header("📚 Documentation")
    
    st.subheader("System Overview")
    st.write("""
    The Electrical Fault Detection and Classification System uses machine learning 
    models trained on 12,000+ simulated power system data points to detect and classify 
    various types of electrical faults.
    """)
    
    st.subheader("Input Parameters")
    st.markdown("""
    - **Ia, Ib, Ic**: Three-phase currents in Amperes (A)
    - **Va, Vb, Vc**: Three-phase voltages in Volts (V)
    """)
    
    st.subheader("Fault Types")
    fault_types = {
        "No Fault": "[0 0 0 0]",
        "LG (Line-to-Ground)": "[1 0 0 1] - Between Phase A and Ground",
        "LL (Line-to-Line)": "[0 0 1 1] - Between Phase A and Phase B",
        "LLG (Line-to-Line-to-Ground)": "[1 0 1 1] - Phases A, B and Ground",
        "LLL (Three-Phase)": "[0 1 1 1] - All three phases",
        "LLLG (Three-Phase-to-Ground)": "[1 1 1 1] - All phases and Ground"
    }
    
    for fault_name, description in fault_types.items():
        st.markdown(f"- **{fault_name}**: {description}")
    
    st.subheader("Model Performance")
    st.markdown("""
    | Metric | Detection | Classification |
    |--------|-----------|-----------------|
    | Accuracy | 99.47% | 99.38% |
    | Error Rate | 0.53% | 0.62% |
    | Model Type | Decision Tree | Polynomial Regression |
    """)
    
    st.subheader("API Endpoints")
    st.code("""
    GET  /              - API Information
    GET  /health        - Health Check
    POST /detect        - Detect Fault Presence
    POST /classify      - Classify Fault Type
    """, language="bash")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Electrical Fault Detection System v1.0 | Powered by FastAPI & Streamlit</p>", 
            unsafe_allow_html=True)
