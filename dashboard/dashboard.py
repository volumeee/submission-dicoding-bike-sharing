import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/main_data.csv')
    
    weather_map = {
        1: 'Clear',
        2: 'Mist/Cloudy',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    }
    data['weather_situation'] = data['weather_situation'].map(weather_map)
    
    data['workingday'] = data['workingday'].map({0: 'Holiday', 1: 'Working Day'})
    
    # Convert 'date' column to datetime
    data['date'] = pd.to_datetime(data['date'])
    
    return data

# Load data
data = load_data()

# Set page title
st.title('Advanced Bike Sharing Analysis Dashboard')

# Sidebar
st.sidebar.header('Dashboard Controls')
weather_filter = st.sidebar.multiselect(
    'Select Weather Condition',
    options=data['weather_situation'].unique(),
    default=data['weather_situation'].unique()
)

workingday_filter = st.sidebar.multiselect(
    'Select Day Type',
    options=['Working Day', 'Holiday'],
    default=['Working Day', 'Holiday']
)

# Date range selector
min_date = data['date'].min().date()
max_date = data['date'].max().date()
start_date, end_date = st.sidebar.date_input(
    'Select Date Range',
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filters
filtered_data = data[
    (data['weather_situation'].isin(weather_filter)) &
    (data['workingday'].isin(workingday_filter)) &
    (data['date'].dt.date >= start_date) &
    (data['date'].dt.date <= end_date)
]

# Check if filtered data is empty
if filtered_data.empty:
    st.warning("No data found for the selected filters. Please adjust your selection.")
else:
    # 1. RFM Analysis
    st.header('1. RFM Analysis')

    latest_date = filtered_data['date'].max()
    rfm = filtered_data.groupby('date').agg({
        'date': 'max',
        'total_count': ['count', 'sum']
    })

    rfm.columns = ['date', 'frequency', 'monetary']
    rfm = rfm.reset_index(drop=True)

    # Calculate recency
    rfm['recency'] = (latest_date - rfm['date']).dt.days

    # Custom function to create bins
    def create_bins(x, n_bins=4):
        min_val = x.min()
        max_val = x.max()
        if min_val == max_val:
            return pd.Series([1] * len(x))
        
        bin_edges = [min_val + i*(max_val-min_val)/n_bins for i in range(n_bins+1)]
        bin_edges[-1] += 0.01  # Add a small value to include the maximum
        return pd.cut(x, bins=bin_edges, labels=False) + 1  # Use 'labels=False' and add 1 to get scores 1-4

    # Create RFM score
    rfm['R'] = create_bins(rfm['recency'], n_bins=4)
    rfm['F'] = create_bins(rfm['frequency'], n_bins=4)
    rfm['M'] = create_bins(rfm['monetary'], n_bins=4)

    # Reverse the order for recency (lower is better)
    rfm['R'] = 5 - rfm['R']

    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

    st.write("RFM Analysis Results:")
    st.write(rfm)

    # Visualize RFM distribution
    rfm_dist = alt.Chart(rfm).mark_circle(size=60).encode(
        x='recency',
        y='frequency',
        color='monetary',
        tooltip=['date', 'recency', 'frequency', 'monetary', 'RFM_Score']
    ).interactive()

    st.altair_chart(rfm_dist, use_container_width=True)

    # 2. Time Series Decomposition
    st.header('2. Time Series Decomposition')

    # Resample data to daily frequency
    daily_data = filtered_data.set_index('date')['total_count'].resample('D').sum().reset_index()

    # Calculate moving average (trend)
    window = 7
    daily_data['trend'] = daily_data['total_count'].rolling(window=window, center=True).mean()

    # Calculate seasonality (difference between actual and trend)
    daily_data['seasonal'] = daily_data['total_count'] - daily_data['trend']

    # Calculate residual
    daily_data['residual'] = daily_data['total_count'] - daily_data['trend'] - daily_data['seasonal']

    # Visualize decomposition
    decomposition = alt.Chart(daily_data).mark_line().encode(
        x='date',
        y='total_count',
        color=alt.value('blue')
    ).properties(
        width=600,
        height=200,
        title='Original Time Series'
    )

    trend = alt.Chart(daily_data).mark_line().encode(
        x='date',
        y='trend',
        color=alt.value('red')
    ).properties(
        width=600,
        height=200,
        title='Trend'
    )

    seasonal = alt.Chart(daily_data).mark_line().encode(
        x='date',
        y='seasonal',
        color=alt.value('green')
    ).properties(
        width=600,
        height=200,
        title='Seasonal'
    )

    residual = alt.Chart(daily_data).mark_line().encode(
        x='date',
        y='residual',
        color=alt.value('purple')
    ).properties(
        width=600,
        height=200,
        title='Residual'
    )

    st.altair_chart(decomposition & trend & seasonal & residual)

    # 3. Simple Clustering (without ML)
    st.header('3. Simple Clustering')

    # We'll use a simple binning approach for clustering
    filtered_data['temp_bin'] = pd.cut(filtered_data['temperature'], bins=5, labels=['Very Cold', 'Cold', 'Mild', 'Warm', 'Hot'])
    filtered_data['humidity_bin'] = pd.cut(filtered_data['humidity'], bins=5, labels=['Very Dry', 'Dry', 'Normal', 'Humid', 'Very Humid'])

    cluster_data = filtered_data.groupby(['temp_bin', 'humidity_bin'])['total_count'].mean().reset_index()

    cluster_heatmap = alt.Chart(cluster_data).mark_rect().encode(
        x='temp_bin:O',
        y='humidity_bin:O',
        color='total_count:Q',
        tooltip=['temp_bin', 'humidity_bin', 'total_count']
    ).properties(
        width=500,
        height=400,
        title='Bike Rental Clusters by Temperature and Humidity'
    )

    st.altair_chart(cluster_heatmap, use_container_width=True)

    # Display raw data
    if st.checkbox('Show Raw Data'):
        st.subheader('Raw Data')
        st.write(filtered_data)