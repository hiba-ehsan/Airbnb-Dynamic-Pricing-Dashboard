import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
from src.data_loader import load_airbnb_data
from src.model import train_demand_model, optimize_price, prepare_features

# Apply blue theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1e3a5f 50%, #0f1419 100%);
    }
   
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f1419 100%);
        border-right: 2px solid #3b82f6;
    }
   
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #93c5fd !important;
    }
   
    /* Regular text */
    .stMarkdown, p, span, label {
        color: #dbeafe !important;
    }
   
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-weight: bold;
    }
   
    [data-testid="stMetricLabel"] {
        color: #3b82f6 !important;
    }
   
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
   
    .stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%);
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.5);
    }
   
    /* Selectbox and inputs */
    .stSelectbox, .stTextInput, .stNumberInput {
        background-color: #1e3a5f;
    }
   
    [data-testid="stSelectbox"] > div > div {
        background-color: #2b4c7c !important;
        border: 1px solid #2563eb;
    }
   
    /* Radio buttons */
    .stRadio > div {
        background-color: transparent;
    }
   
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e3a5f !important;
        color: #93c5fd !important;
        border: 1px solid #2563eb;
        border-radius: 8px;
    }
   
    /* Info, success, warning boxes */
    .stAlert {
        background-color: #1e3a5f;
        border: 1px solid #2563eb;
        border-radius: 8px;
    }
   
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #2563eb;
        border-radius: 8px;
    }
   
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1e3a5f;
        border: 2px dashed #2563eb;
        border-radius: 8px;
        padding: 10px;
    }
   
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e3a5f;
        border-radius: 8px;
    }
   
    .stTabs [data-baseweb="tab"] {
        color: #93c5fd;
    }
   
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
    }
   
    /* Slider */
    .stSlider > div > div > div {
        background-color: #2563eb !important;
    }
   
    /* Progress bar */
    .stProgress > div > div {
        background-color: #2563eb !important;
    }
   
    /* Cards/containers */
    [data-testid="stVerticalBlock"] > div {
        border-radius: 8px;
    }
   
    /* Links */
    a {
        color: #3b82f6 !important;
    }
   
    a:hover {
        color: #60a5fa !important;
    }
   
    /* Caption */
    .stCaption {
        color: #3b82f6 !important;
    }
   
    /* Divider */
    hr {
        border-color: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("ML Price Prediction & Simulation")
st.markdown("Train demand models and simulate booking predictions for different price scenarios")

# Explanation of calculations
with st.expander("**Explanation of calculations.**", expanded=True):
    st.markdown("""
    **XGBoost Regression Model**
    
    We predict booking demand as a non-linear function of price and other features using gradient boosting:
    
    $$y = f(price, competitor\\_price, time\\_features, room\\_type, ...)$$
    
    - **Feature Importance:** Shows which factors most influence demand
    - **R-squared:** How well the model fits the data (higher is better)
    - **MAE:** Mean Absolute Error in occupancy prediction
    
    **Revenue Calculation:**
    $$Revenue = predicted\\_occupancy \\times price$$
    
    **Linear OLS Alternative:**
    For comparison, linear regression provides interpretable coefficients.
    """)

# Load data
if 'airbnb_data' in st.session_state:
    df = st.session_state['airbnb_data']
else:
    df = load_airbnb_data()

if df is None or df.empty:
    st.error("No Airbnb data available. Please provide a dataset.")
    st.stop()

# Model settings
st.sidebar.header("Model Settings")
# Check XGBoost availability
try:
    from xgboost import XGBRegressor
    model_options = ['xgboost', 'linear']
    default_index = 0
except ImportError:
    model_options = ['linear']
    default_index = 0

model_type = st.sidebar.selectbox("Choose model type", model_options, index=default_index, 
                                  help="XGBoost for better predictions, Linear for interpretability")
st.sidebar.info(f"Using {model_type.upper()} model for demand prediction")

# Listing selection (if listing id exists)
listing_col = None
for c in ['id','listing_id','listingid']:
    if c in df.columns:
        listing_col = c
        break

selected_listing = None
if listing_col:
    listing_choices = df[listing_col].unique().tolist()
    selected_listing = st.sidebar.selectbox("Choose listing (optional)", [None] + listing_choices)

# Train model
st.header("Train Demand Model")
if st.button("Train Model"):
    with st.spinner("Training demand model..."):
        model, scaler, metrics = train_demand_model(df, model_type=model_type)
        if model is None:
            st.error("Model training failed or insufficient data")
        else:
            st.success("Model trained")
            st.write(metrics)
            st.session_state['demand_model'] = (model, scaler, metrics)

# Price simulation
st.header("Price Simulation")
# Use median if available, otherwise default to 1.0
median_price = float(df['our_current_price'].median()) if 'our_current_price' in df.columns and not df['our_current_price'].isna().all() else 1.0
price_input = st.number_input("Test Price ($)", min_value=1.0, value=median_price)
if st.button("Run Simulation"):
    if 'demand_model' not in st.session_state:
        st.warning("Please train a model first")
    else:
        model, scaler, metrics = st.session_state['demand_model']
        # Use optimize_price to run price sensitivity using trained model type
        result = optimize_price(df, room_type=None, target_occupancy=0.85, model_type=model_type)
        if result:
            st.subheader("Optimization Result (global)")
            st.write({
                'current_price': result['current_price'],
                'recommended_price': result['recommended_price'],
                'predicted_revenue': result['predicted_revenue'],
                'revenue_improvement_pct': result['revenue_improvement_pct']
            })
        else:
            st.error("Failed to compute optimization")

# Single listing prediction (if applicable)
if selected_listing:
    st.header("Single Listing Predictions")
    idx = df[df[listing_col] == selected_listing].index
    if len(idx) > 0:
        sample = df.loc[idx[0]]
        st.write(sample[['our_current_price','competitor_price','occupancy_rate','revenue']])
        # Simple price sensitivity: vary price + or - 30%
        base_price = sample['our_current_price']
        price_range = [base_price * x for x in [0.7, 0.85, 1.0, 1.15, 1.3]]
        sim = []
        for p in price_range:
            temp = df.copy()
            temp.loc[temp[listing_col] == selected_listing, 'our_current_price'] = p
            res = optimize_price(temp, room_type=None, model_type=model_type)
            if res:
                sim.append({'price': p, 'predicted_revenue': res['predicted_revenue']})
        if sim:
            st.table(sim)
        else:
            st.info("Not enough data to simulate single listing")
                        
