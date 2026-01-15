import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_airbnb_data
from src.visualization import plot_price_comparison, plot_price_elasticity, plot_boxplot_by_day

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

st.title("Airbnb Price Analysis")
st.markdown("Explore price distributions, neighborhood comparisons, and price elasticity for Airbnb listings")

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
if 'city' in df.columns:
    selected_cities = st.sidebar.multiselect("City", options=df['city'].unique().tolist(), default=None)
    if selected_cities:
        df = df[df['city'].isin(selected_cities)]

# Basic stats
st.header("Price Statistics")
# Ensure we have a price column to work with
if 'our_current_price' not in df.columns:
    if 'price' in df.columns:
        df['our_current_price'] = df['price']
    else:
        st.warning("Price column not found. Price statistics and charts will be disabled for this dataset.")

col1, col2, col3, col4 = st.columns(4)
if 'our_current_price' in df.columns and not df['our_current_price'].isna().all():
    col1.metric("Mean Price", f"${df['our_current_price'].mean():.0f}")
    col2.metric("Median Price", f"${df['our_current_price'].median():.0f}")
    col3.metric("Min Price", f"${df['our_current_price'].min():.0f}")
    col4.metric("Max Price", f"${df['our_current_price'].max():.0f}")
else:
    col1.metric("Mean Price", "N/A")
    col2.metric("Median Price", "N/A")
    col3.metric("Min Price", "N/A")
    col4.metric("Max Price", "N/A")

# Price distribution
st.subheader("Price Distribution")
fig_price = None
try:
    fig_price = plot_price_comparison(df)
except Exception:
    fig_price = None

if fig_price:
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("Price comparison visualization not available for this dataset")

# Neighborhood / Group Price Distribution
st.subheader("Neighborhood / Group Price Distribution")
# Detect potential grouping columns
candidate_cols = [c for c in ['neighbourhood_cleansed','neighbourhood','neighborhood','neighborhood_group_cleansed','city','region'] if c in df.columns]

group_options = []
if candidate_cols:
    group_options += candidate_cols
# Provide a price-bucket fallback and an option to view all listings
group_options += ['price_bucket', 'all_listings']

selected_group = st.selectbox("Group by", options=group_options, index=0 if candidate_cols else 1,
                             help='Choose a column to group prices by, or use price buckets as a fallback')

if selected_group == 'all_listings':
    st.info("Showing distribution for all listings")
    fig = px.box(df, y='our_current_price', points='outliers', title='Price Distribution - All Listings')
    st.plotly_chart(fig, use_container_width=True)

elif selected_group == 'price_bucket':
    df = df.copy()
    try:
        df['price_bucket'] = pd.qcut(df['our_current_price'], q=5, labels=['Very Low','Low','Medium','High','Very High'])
    except Exception:
        df['price_bucket'] = pd.cut(df['our_current_price'], bins=5, labels=['Very Low','Low','Medium','High','Very High'])

    top_n = st.slider("Top N price buckets to display", 1, 5, 5)
    buckets = list(df['price_bucket'].cat.categories) if hasattr(df['price_bucket'], 'cat') else sorted(df['price_bucket'].unique())
    display_buckets = buckets[:top_n]
    box_df = df[df['price_bucket'].isin(display_buckets)]

    if box_df.empty:
        st.info("No data available for selected price buckets")
    else:
        fig = px.box(box_df, x='price_bucket', y='our_current_price', points='outliers',
                     title='Price Distribution by Price Bucket', category_orders={'price_bucket': buckets})
        st.plotly_chart(fig, use_container_width=True)

else:
    grouped_col = selected_group
    top_n = st.slider("Top N groups to display", 3, 50, 8)
    top_groups = df[grouped_col].value_counts().nlargest(top_n).index.tolist()
    box_df = df[df[grouped_col].isin(top_groups)]

    if box_df.empty:
        st.info(f"No data available for selected group: {grouped_col}")
    else:
        fig = px.box(box_df, x=grouped_col, y='our_current_price', points='outliers',
                     title=f'Price Distribution by {grouped_col}', category_orders={grouped_col: top_groups})
        st.plotly_chart(fig, use_container_width=True)

# Price elasticity
st.header("Price Elasticity")
fig_elasticity = plot_price_elasticity(df)
if fig_elasticity:
    st.plotly_chart(fig_elasticity, use_container_width=True)
else:
    st.info("Price elasticity plot requires 'our_current_price' and 'bookings' columns")

with st.expander("📋 Sample Data"):
    st.dataframe(df.head(10), use_container_width=True)
