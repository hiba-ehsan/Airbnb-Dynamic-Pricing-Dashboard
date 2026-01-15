import streamlit as st
import pandas as pd
from src.data_loader import load_data, process_data, load_airbnb_data

st.set_page_config(  
    page_title="End-to-End Airbnb Pricing Dashboard (By: Hiba Ehsan)",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded")

# Blue Theme (Modern and professional)
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

st.markdown("""
<style>
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🏠 Airbnb Dynamic Pricing Dashboard")
st.markdown("*Make smarter pricing decisions with data-driven insights*")
st.caption("DSC327 Data Visualization Project | USA Airbnb Dataset via Kaggle | By: Hiba Ehsan | SP24-BST-012")


st.sidebar.header("📤 Data Source")
data_source = st.sidebar.radio(
    "Choose data source",
    options=["Sample Data (CSV)", "Upload CSV", "Database"],
    help="Select where to load data from"
)

df = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Airbnb pricing CSV",
        type=['csv'],
        help="CSV should contain the columns for date, listing_id, price, available, neighbourhood, room_type, & number_of_reviews"
    )
   
    if uploaded_file is not None:
        try:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
           
            if df is not None:
                df = process_data(df)
                st.sidebar.success(f"Loaded {len(df):,} records")
                st.session_state['uploaded_data'] = df
            else:
                st.sidebar.error("Could not read CSV file")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
   
   
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
    else:
        st.info("Please upload a CSV file in the sidebar")
        st.stop()
elif data_source == "Database":
    use_db = True
    df = load_data(use_db=use_db)
    if df.empty:
        st.warning("WARNING: Database connection failed or no data available. Using sample data.")
        df = load_data(use_db=False)
else:
    df = load_airbnb_data()



if df is not None and not df.empty:
    if 'revenue' not in df.columns:
        if 'bookings' in df.columns and 'our_current_price' in df.columns:
            df['revenue'] = df['bookings'] * df['our_current_price']
        

        elif 'number_of_reviews' in df.columns and 'price' in df.columns:
            df['bookings'] = (df['number_of_reviews'] * 1.39).round()
            df['revenue'] = df['bookings'] * df['price']
        
        
        elif 'availability_365' in df.columns and 'price' in df.columns:
            occupied = (365 - df['availability_365']).clip(lower=0)
            df['revenue'] = occupied * df['price']
        
        else:
            df['revenue'] = 0
    
    #Handling missing values
    df['revenue'] = df['revenue'].fillna(0)


if df is not None and not df.empty:
    st.session_state['airbnb_data'] = df
    st.session_state['hotel_data'] = df  


st.sidebar.header("NAVIAGATION BAR")
st.sidebar.markdown("Use the pages above to explore:")
st.sidebar.markdown("📊 Overview: Airbnb key metrics and time-series analysis")
st.sidebar.markdown(" Price Analysis: Price distributions and neighborhood comparisons")
st.sidebar.markdown(" ML Price Prediction: Predict demand and simulate price scenarios")
st.sidebar.markdown(" Price Optimization: ML-powered price recommendations")
st.sidebar.markdown("🎨 Visualization Gallery: Airbnb-specific visualizations")

#Homepage 
if df is not None and not df.empty:
    st.header(" Kindly check my R Project too after this :((")
    st.markdown("""
    This dashboard helps you analyze and optimize **Airbnb listing** pricing using:
    - **Time-series analysis** for identifying trends & seaosinality
    - **Machine learning** for price optimization and forecasting the demand
    - **Interactive visualizations** from multiple libraries
    - **What-if simulations** for revenue and occupancy planning 
   
    ### Quick Stats
    """)

    #ensure required columns exist
    if 'our_current_price' not in df.columns:
        if 'price' in df.columns:
            df['our_current_price'] = df['price']
        else:
            st.warning("Dataset missing 'our_current_price' or 'price' column; price metrics will show N/A")

  
    if 'date' not in df.columns or df['date'].isna().all():
        if 'last_review' in df.columns:
            df['date'] = pd.to_datetime(df['last_review'], errors='coerce').fillna(pd.Timestamp.today())
        else:
            df['date'] = pd.Timestamp.today()
    else:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Compute revenue if missing but also possible to compute
    if 'revenue' not in df.columns and 'bookings' in df.columns and 'our_current_price' in df.columns:
        df['revenue'] = df['our_current_price'] * df['bookings']

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{len(df):,}")

    #Safe Date Range metric
    try:
        if 'date' in df.columns and df['date'].notna().any():
            days = (df['date'].max() - df['date'].min()).days + 1
            date_range_str = f"{days} days"
        else:
            date_range_str = "N/A"
    except Exception:
        date_range_str = "N/A"
    col2.metric("Date Range", date_range_str)

    # Safe Listing Types metric
    try:
        listing_types = len(df['room_type'].unique()) if 'room_type' in df.columns else 'N/A'
    except Exception:
        listing_types = 'N/A'
    col3.metric("Listing Types", listing_types)


    st.info("💡 **Tip:** Use the sidebar to switch between data sources or navigate to specific analysis pages.")

    # Data preview
    with st.expander("📋 Preview Data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
else:
    st.warning("WARNING: No data loaded. Please check your data source or upload a CSV file.")
