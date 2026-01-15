import streamlit as st
from src.data_loader import load_airbnb_data
from src.visualization import (
    plot_price_comparison, plot_revenue_trend, plot_demand_heatmap,
    plot_3d_scatter, plot_correlation_heatmap, plot_boxplot_by_day, plot_price_elasticity
)
from src.multiviz import (
    plot_altair_revenue_by_room, plot_altair_price_scatter, plot_seaborn_regression
)

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

st.title("🎨 Airbnb Visualization Gallery")
st.markdown("Explore Airbnb-specific visualizations using multiple libraries")

# Load data
if 'airbnb_data' in st.session_state:
    df = st.session_state['airbnb_data']
else:
    df = load_airbnb_data()

if df is None or df.empty:
    st.error("No data available. Please upload or provide Airbnb CSV.")
    st.stop()

# Filters
st.sidebar.header("Filters")
if 'room_type' in df.columns:
    selected_rooms = st.sidebar.multiselect("Listing Types", options=df['room_type'].unique().tolist(), default=None)
    if selected_rooms:
        df = df[df['room_type'].isin(selected_rooms)]

st.header("Core Visualizations")

try:
    fig = plot_price_comparison(df)
    if fig:
        st.subheader("Price Comparison")
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Price comparison not available")

try:
    fig = plot_revenue_trend(df)
    if fig:
        st.subheader("Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Revenue trend not available")

try:
    fig = plot_demand_heatmap(df)
    if fig:
        st.subheader("Occupancy Heatmap")
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Occupancy heatmap not available")

# Additional charts
st.subheader("Additional Charts")
try:
    fig = plot_price_elasticity(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Price elasticity not available")

try:
    img = plot_boxplot_by_day(df, column='our_current_price')
    if img:
        st.image(f"data:image/png;base64,{img}", use_container_width=True)
except Exception:
    st.info("Boxplot not available")

with st.expander("📋 Sample Data"):
    st.dataframe(df.head(10), use_container_width=True)
