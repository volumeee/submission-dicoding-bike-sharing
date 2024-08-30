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
    
    # Convert temperature to Celsius
    data['temperature'] = data['temperature'] * 41 - 8
    data['feels_like_temperature'] = data['feels_like_temperature'] * 50 - 16
    
    # Convert humidity to percentage
    data['humidity'] = data['humidity'] * 100
    
    return data

# Load data
data = load_data()

# Set page title
st.title('Advanced Bike Sharing Analysis Dashboard')

# Sidebar
st.sidebar.header('Dashboard Controls')

# Weather filter
weather_filter = st.sidebar.multiselect(
    'Select Weather Condition',
    options=data['weather_situation'].unique(),
    default=data['weather_situation'].unique()
)

# Working day filter
workingday_filter = st.sidebar.multiselect(
    'Select Day Type',
    options=data['workingday'].unique(),
    default=data['workingday'].unique()
)

# Date range selector
min_date = data['date'].min().date()
max_date = data['date'].max().date()
start_date, end_date = st.sidebar.date_input(
    'Select Date Range',
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date,
    key='date_range'
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
    # Main content
    st.header('1. Pengaruh Cuaca terhadap Jumlah Peminjaman Sepeda')

    weather_chart = alt.Chart(filtered_data).mark_boxplot().encode(
        x='weather_situation:O',
        y='total_count:Q',
        color='weather_situation:N'
    ).properties(
        width=600,
        height=400,
        title='Distribusi Jumlah Peminjaman Berdasarkan Kondisi Cuaca'
    )

    st.altair_chart(weather_chart, use_container_width=True)

    weather_avg = filtered_data.groupby('weather_situation')['total_count'].mean().sort_values(ascending=False)
    best_weather = weather_avg.index[0]
    worst_weather = weather_avg.index[-1]

    st.write(f"""
    Berdasarkan data yang difilter dari {start_date} hingga {end_date}, terlihat bahwa kondisi cuaca mempengaruhi jumlah peminjaman sepeda:
    - Cuaca "{best_weather}" menghasilkan jumlah peminjaman tertinggi dengan rata-rata {weather_avg[best_weather]:.2f} peminjaman.
    - Cuaca "{worst_weather}" menghasilkan jumlah peminjaman terendah dengan rata-rata {weather_avg[worst_weather]:.2f} peminjaman.
    - Perbedaan antara kondisi cuaca terbaik dan terburuk adalah {weather_avg[best_weather] - weather_avg[worst_weather]:.2f} peminjaman.
    """)

    st.header('2. Perbedaan Jumlah Peminjaman pada Hari Kerja dan Hari Libur')

    workingday_chart = alt.Chart(filtered_data).mark_boxplot().encode(
        x='workingday:N',
        y='total_count:Q',
        color='workingday:N'
    ).properties(
        width=600,
        height=400,
        title='Distribusi Jumlah Peminjaman: Hari Kerja vs Hari Libur'
    )

    st.altair_chart(workingday_chart, use_container_width=True)

    workingday_avg = filtered_data.groupby('workingday')['total_count'].mean()

    if 'Working Day' in workingday_avg.index and 'Holiday' in workingday_avg.index:
        st.write(f"""
        Berdasarkan data yang difilter, terdapat perbedaan dalam distribusi jumlah peminjaman sepeda antara hari kerja dan hari libur:
        - Rata-rata peminjaman pada hari kerja adalah {workingday_avg['Working Day']:.2f}.
        - Rata-rata peminjaman pada hari libur adalah {workingday_avg['Holiday']:.2f}.
        - {'Hari kerja' if workingday_avg['Working Day'] > workingday_avg['Holiday'] else 'Hari libur'} memiliki rata-rata peminjaman yang lebih tinggi.
        - Perbedaan rata-rata peminjaman antara hari kerja dan hari libur adalah {abs(workingday_avg['Working Day'] - workingday_avg['Holiday']):.2f}.
        """)
    elif 'Working Day' in workingday_avg.index:
        st.write(f"""
        Berdasarkan data yang difilter, hanya terdapat informasi untuk hari kerja:
        - Rata-rata peminjaman pada hari kerja adalah {workingday_avg['Working Day']:.2f}.
        """)
    elif 'Holiday' in workingday_avg.index:
        st.write(f"""
        Berdasarkan data yang difilter, hanya terdapat informasi untuk hari libur:
        - Rata-rata peminjaman pada hari libur adalah {workingday_avg['Holiday']:.2f}.
        """)
    else:
        st.write("Tidak ada data yang tersedia untuk hari kerja atau hari libur berdasarkan filter yang dipilih.")

    st.header('3. Tren Peminjaman Sepeda Sepanjang Hari')

    hourly_avg = filtered_data.groupby(['hour', 'workingday'])['total_count'].mean().reset_index()

    daily_trend_chart = alt.Chart(hourly_avg).mark_line().encode(
        x='hour:O',
        y='total_count:Q',
        color='workingday:N',
        tooltip=['hour', 'workingday', 'total_count']
    ).properties(
        width=600,
        height=400,
        title='Daily Trend of Bike Rentals'
    )

    st.altair_chart(daily_trend_chart, use_container_width=True)

    workday_data = hourly_avg[hourly_avg['workingday'] == 'Working Day']
    holiday_data = hourly_avg[hourly_avg['workingday'] == 'Holiday']

    if not workday_data.empty:
        peak_hour_workday = workday_data['total_count'].idxmax()
        peak_workday_info = f"Puncak peminjaman terjadi pada pukul {workday_data.loc[peak_hour_workday, 'hour']}:00 dengan rata-rata {workday_data.loc[peak_hour_workday, 'total_count']:.2f} peminjaman."
    else:
        peak_workday_info = "Tidak ada data untuk hari kerja."

    if not holiday_data.empty:
        peak_hour_holiday = holiday_data['total_count'].idxmax()
        peak_holiday_info = f"Puncak peminjaman terjadi pada pukul {holiday_data.loc[peak_hour_holiday, 'hour']}:00 dengan rata-rata {holiday_data.loc[peak_hour_holiday, 'total_count']:.2f} peminjaman."
    else:
        peak_holiday_info = "Tidak ada data untuk hari libur."

    st.write(f"""
    Grafik ini menunjukkan tren peminjaman sepeda sepanjang hari untuk hari kerja dan hari libur berdasarkan data yang difilter:
    - Hari Kerja:
        - {peak_workday_info}
        - Terlihat dua puncak utama yang mencerminkan pola commuting.
    - Hari Libur:
        - {peak_holiday_info}
        - Tren lebih merata sepanjang hari, mungkin mencerminkan penggunaan untuk rekreasi.
    - Kedua tipe hari menunjukkan penurunan penggunaan di malam hari.
    """)

    # RFM Analysis
    st.header('4. RFM Analysis')

    # Ensure 'date' is in datetime format
    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
    filtered_data['datetime'] = filtered_data['date'] + pd.to_timedelta(filtered_data['hour'], unit='h')

    # Calculate recency, frequency, and monetary values
    today = filtered_data['datetime'].max() + pd.Timedelta(hours=1)
    rfm = filtered_data.groupby('hour').agg({
        'datetime': lambda x: (today - x.max()).total_seconds() / 3600,  # Recency in hours
        'record_id': 'count',  # Frequency
        'total_count': 'sum'  # Monetary (total bike rentals)
    })

    # Rename columns
    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    # Normalize RFM values
    def normalize(x):
        if x.max() == x.min():
            return x - x.min()
        return (x - x.min()) / (x.max() - x.min())

    rfm_normalized = rfm.apply(normalize)

    # Invert Recency (lower values are better)
    rfm_normalized['Recency'] = 1 - rfm_normalized['Recency']

    # Calculate RFM Score
    rfm['RFM_Score'] = (rfm_normalized['Recency'] * 0.2 + 
                        rfm_normalized['Frequency'] * 0.4 + 
                        rfm_normalized['Monetary'] * 0.4)

    # Visualization using Altair
    rfm_chart = alt.Chart(rfm.reset_index()).mark_circle().encode(
        x='Recency',
        y='Frequency',
        size='Monetary',
        color='RFM_Score:Q',
        tooltip=['hour', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']
    ).properties(
        width=600,
        height=400,
        title='RFM Analysis by Hour'
    )

    st.altair_chart(rfm_chart, use_container_width=True)

    # Display statistics
    st.write(rfm.describe())
    st.write("\nRFM Score Range:", rfm['RFM_Score'].min(), "-", rfm['RFM_Score'].max())

    st.write(f"""
    Berdasarkan analisis RFM:
    - Recency: Nilai berkisar dari {rfm['Recency'].min():.2f} hingga {rfm['Recency'].max():.2f} jam.
    - Frequency: Nilai berkisar dari {rfm['Frequency'].min():.0f} hingga {rfm['Frequency'].max():.0f} penyewaan.
    - Monetary: Nilai berkisar dari {rfm['Monetary'].min():.2f} hingga {rfm['Monetary'].max():.2f} total penyewaan sepeda.
    - Skor RFM tertinggi adalah {rfm['RFM_Score'].max():.2f}, menunjukkan jam yang paling berharga.
    - Skor RFM terendah adalah {rfm['RFM_Score'].min():.2f}, yang mungkin memerlukan strategi perbaikan khusus.
    """)

    # Wawasan tambahan
    best_hour = rfm['RFM_Score'].idxmax()
    worst_hour = rfm['RFM_Score'].idxmin()

    st.write(f"""
    Wawasan tambahan:
    - Jam paling berharga adalah {best_hour}:00, dengan Skor RFM {rfm['RFM_Score'].max():.2f}.
    - Jam paling kurang berharga adalah {worst_hour}:00, dengan Skor RFM {rfm['RFM_Score'].min():.2f}.
    - Jam-jam dengan skor RFM tinggi mungkin merupakan target yang baik untuk promosi atau peningkatan ketersediaan layanan.
    - Jam-jam dengan skor RFM rendah mungkin memerlukan strategi untuk meningkatkan penyewaan sepeda, seperti diskon khusus di luar jam sibuk.
    """)


    # Time Series Decomposition
    st.header('5. Time Series Decomposition')

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

    st.write(f"""
    Analisis dekomposisi time series menunjukkan:
    - Tren: Terlihat adanya {' peningkatan' if daily_data['trend'].iloc[-1] > daily_data['trend'].iloc[0] else ' penurunan'} umum dalam jumlah peminjaman sepeda selama periode yang dipilih.
    - Musiman: Pola musiman menunjukkan fluktuasi {' harian' if len(daily_data) > 7 else ' mingguan'} dalam peminjaman sepeda.
    - Residual: Komponen residual menangkap variasi yang tidak dapat dijelaskan oleh tren atau musiman, yang mungkin disebabkan oleh faktor-faktor eksternal atau acak.
    """)

    # Simple Clustering
    st.header('6. Simple Clustering')

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
        title='Heatmap of Average Bike Rentals by Temperature and Humidity'
    )

    st.altair_chart(cluster_heatmap, use_container_width=True)

    # Find the cluster with the highest average rentals
    max_cluster = cluster_data.loc[cluster_data['total_count'].idxmax()]
    min_cluster = cluster_data.loc[cluster_data['total_count'].idxmin()]

    st.write(f"""
    Analisis clustering sederhana menunjukkan:
    - Cluster dengan peminjaman tertinggi: {max_cluster['temp_bin']} temperature dan {max_cluster['humidity_bin']} humidity, dengan rata-rata {max_cluster['total_count']:.2f} peminjaman.
    - Cluster dengan peminjaman terendah: {min_cluster['temp_bin']} temperature dan {min_cluster['humidity_bin']} humidity, dengan rata-rata {min_cluster['total_count']:.2f} peminjaman.
    - Perbedaan antara cluster tertinggi dan terendah adalah {max_cluster['total_count'] - min_cluster['total_count']:.2f} peminjaman.
    """)

    # Correlation Analysis
    st.header('7. Correlation Analysis')

    # Select numeric columns for correlation
    numeric_columns = ['temperature', 'feels_like_temperature', 'humidity', 'windspeed', 'total_count']
    corr_data = filtered_data[numeric_columns]

    # Calculate correlation matrix
    corr_matrix = corr_data.corr()

    # Create a heatmap of the correlation matrix
    corr_heatmap = alt.Chart(corr_matrix.reset_index().melt('index')).mark_rect().encode(
        x='index:O',
        y='variable:O',
        color='value:Q',
        tooltip=['index', 'variable', 'value']
    ).properties(
        width=500,
        height=400,
        title='Correlation Heatmap of Numeric Variables'
    )

    st.altair_chart(corr_heatmap, use_container_width=True)

    # Find the highest positive and negative correlations with total_count
    correlations = corr_matrix['total_count'].sort_values(ascending=False)
    highest_pos_corr = correlations.iloc[1]  # Exclude self-correlation
    highest_neg_corr = correlations.iloc[-1]

    st.write(f"""
    Analisis korelasi menunjukkan:
    - Variabel dengan korelasi positif tertinggi terhadap jumlah peminjaman: {correlations.index[1]} ({highest_pos_corr:.2f})
    - Variabel dengan korelasi negatif tertinggi terhadap jumlah peminjaman: {correlations.index[-1]} ({highest_neg_corr:.2f})
    - Suhu memiliki korelasi {' positif ' if corr_matrix['temperature']['total_count'] > 0 else ' negatif '} dengan jumlah peminjaman.
    - Kelembaban memiliki korelasi {' positif ' if corr_matrix['humidity']['total_count'] > 0 else ' negatif '} dengan jumlah peminjaman.
    """)

    # Conclusion
    st.header('8. Kesimpulan dan Rekomendasi')

    st.write("""
    Berdasarkan analisis yang telah dilakukan, beberapa kesimpulan dan rekomendasi yang dapat diambil:

    1. Pengaruh Cuaca:
       - Cuaca yang cerah cenderung menghasilkan peminjaman sepeda yang lebih tinggi.
       - Rekomendasi: Tingkatkan ketersediaan sepeda pada hari-hari dengan prakiraan cuaca baik.

    2. Hari Kerja vs Hari Libur:
       - Terdapat perbedaan pola peminjaman antara hari kerja dan hari libur.
       - Rekomendasi: Sesuaikan strategi distribusi sepeda berdasarkan tipe hari.

    3. Tren Harian:
       - Terdapat puncak peminjaman pada jam-jam tertentu, terutama pada hari kerja.
       - Rekomendasi: Pastikan ketersediaan sepeda maksimal pada jam-jam puncak.

    4. Analisis RFM:
       - Identifikasi segmen pelanggan berdasarkan frekuensi dan nilai peminjaman.
       - Rekomendasi: Kembangkan program loyalitas untuk pelanggan dengan skor RFM tinggi.

    5. Dekomposisi Time Series:
       - Terdapat pola musiman dalam peminjaman sepeda.
       - Rekomendasi: Antisipasi fluktuasi permintaan berdasarkan pola musiman yang teridentifikasi.

    6. Clustering:
       - Kondisi cuaca tertentu (suhu dan kelembaban) memiliki pengaruh signifikan terhadap peminjaman.
       - Rekomendasi: Optimalkan layanan berdasarkan prakiraan kondisi cuaca.

    7. Korelasi:
       - Faktor cuaca memiliki korelasi yang signifikan dengan jumlah peminjaman.
       - Rekomendasi: Gunakan data cuaca untuk memprediksi dan mengantisipasi permintaan.

    Implementasi rekomendasi ini diharapkan dapat meningkatkan efisiensi layanan dan kepuasan pelanggan.
    """)

    # Add a footer
    st.markdown("---")
    st.markdown("Dashboard created by bagus erwanto")
    st.markdown("Data last updated on: " + str(data['date'].max().date()))
