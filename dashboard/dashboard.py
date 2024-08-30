import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# Load and preprocess data
@st.cache_data
def load_data():
    data = pd.read_csv('dashboard/main_data.csv')
    
    weather_map = {1: 'Clear', 2: 'Mist/Cloudy', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'}
    data['weather_situation'] = data['weather_situation'].map(weather_map)
    data['workingday'] = data['workingday'].map({0: 'Holiday', 1: 'Working Day'})
    
    data['date'] = pd.to_datetime(data['date'])
    data['temperature'] = data['temperature'] * 41 - 8
    data['feels_like_temperature'] = data['feels_like_temperature'] * 50 - 16
    data['humidity'] = data['humidity'] * 100
    
    return data

# Main function
def main():
    st.title('Advanced Bike Sharing Analysis Dashboard')
    
    data = load_data()
    
    # Sidebar filters
    st.sidebar.header('Dashboard Controls')
    weather_filter = st.sidebar.multiselect('Select Weather Condition', options=data['weather_situation'].unique(), default=data['weather_situation'].unique())
    workingday_filter = st.sidebar.multiselect('Select Day Type', options=data['workingday'].unique(), default=data['workingday'].unique())
    
    min_date, max_date = data['date'].min().date(), data['date'].max().date()
    start_date, end_date = st.sidebar.date_input('Select Date Range', [min_date, max_date], min_value=min_date, max_value=max_date, key='date_range')
    
    # Filter data
    filtered_data = data[
        (data['weather_situation'].isin(weather_filter)) &
        (data['workingday'].isin(workingday_filter)) &
        (data['date'].dt.date >= start_date) &
        (data['date'].dt.date <= end_date)
    ]
    
    if filtered_data.empty:
        st.warning("No data found for the selected filters. Please adjust your selection.")
        return
    
    # Analysis sections
    weather_analysis(filtered_data, start_date, end_date)
    workingday_analysis(filtered_data)
    daily_trend_analysis(filtered_data)
    rfm_analysis(filtered_data)
    time_series_decomposition(filtered_data)
    clustering_analysis(filtered_data)
    correlation_analysis(filtered_data)
    conclusion_and_recommendations()
    
    # Footer
    st.markdown("---")
    st.markdown("Dashboard created by bagus erwanto")
    st.markdown(f"Data last updated on: {data['date'].max().date()}")

# Analysis functions
def weather_analysis(filtered_data, start_date, end_date):
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
    best_weather, worst_weather = weather_avg.index[0], weather_avg.index[-1]
    
    st.write(f"""
    Berdasarkan data yang difilter dari {start_date} hingga {end_date}, terlihat bahwa kondisi cuaca mempengaruhi jumlah peminjaman sepeda:
    - Cuaca "{best_weather}" menghasilkan jumlah peminjaman tertinggi dengan rata-rata {weather_avg[best_weather]:.2f} peminjaman.
    - Cuaca "{worst_weather}" menghasilkan jumlah peminjaman terendah dengan rata-rata {weather_avg[worst_weather]:.2f} peminjaman.
    - Perbedaan antara kondisi cuaca terbaik dan terburuk adalah {weather_avg[best_weather] - weather_avg[worst_weather]:.2f} peminjaman.
    """)

def workingday_analysis(filtered_data):
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
        Berdasarkan data yang difilter:
        - Rata-rata peminjaman pada hari kerja adalah {workingday_avg['Working Day']:.2f}.
        - Rata-rata peminjaman pada hari libur adalah {workingday_avg['Holiday']:.2f}.
        - {'Hari kerja' if workingday_avg['Working Day'] > workingday_avg['Holiday'] else 'Hari libur'} memiliki rata-rata peminjaman yang lebih tinggi.
        - Perbedaan rata-rata peminjaman antara hari kerja dan hari libur adalah {abs(workingday_avg['Working Day'] - workingday_avg['Holiday']):.2f}.
        """)
    else:
        st.write("Tidak cukup data untuk membandingkan hari kerja dan hari libur.")

def daily_trend_analysis(filtered_data):
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
    
    peak_workday_info = "Tidak ada data untuk hari kerja." if workday_data.empty else f"Puncak peminjaman terjadi pada pukul {workday_data.loc[workday_data['total_count'].idxmax(), 'hour']}:00 dengan rata-rata {workday_data['total_count'].max():.2f} peminjaman."
    peak_holiday_info = "Tidak ada data untuk hari libur." if holiday_data.empty else f"Puncak peminjaman terjadi pada pukul {holiday_data.loc[holiday_data['total_count'].idxmax(), 'hour']}:00 dengan rata-rata {holiday_data['total_count'].max():.2f} peminjaman."
    
    st.write(f"""
    Grafik ini menunjukkan tren peminjaman sepeda sepanjang hari untuk hari kerja dan hari libur berdasarkan data yang difilter:
    - Hari Kerja: {peak_workday_info}
    - Hari Libur: {peak_holiday_info}
    - Kedua tipe hari menunjukkan penurunan penggunaan di malam hari.
    """)

def rfm_analysis(filtered_data):
    st.header('4. RFM Analysis')
    
    filtered_data['datetime'] = filtered_data['date'] + pd.to_timedelta(filtered_data['hour'], unit='h')
    today = filtered_data['datetime'].max() + pd.Timedelta(hours=1)
    
    rfm = filtered_data.groupby('hour').agg({
        'datetime': lambda x: (today - x.max()).total_seconds() / 3600,
        'record_id': 'count',
        'total_count': 'sum'
    }).rename(columns={'datetime': 'Recency', 'record_id': 'Frequency', 'total_count': 'Monetary'})
    
    rfm_normalized = rfm.apply(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x - x.min())
    rfm_normalized['Recency'] = 1 - rfm_normalized['Recency']
    
    rfm['RFM_Score'] = (rfm_normalized['Recency'] * 0.2 + 
                        rfm_normalized['Frequency'] * 0.4 + 
                        rfm_normalized['Monetary'] * 0.4)
    
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
    
    st.write(rfm.describe())
    st.write("\nRFM Score Range:", rfm['RFM_Score'].min(), "-", rfm['RFM_Score'].max())
    
    best, worst_hour = rfm['RFM_Score'].idxmax(), rfm['RFM_Score'].idxmin()
    
    st.write(f"""
    Berdasarkan analisis RFM:
    - Recency: Nilai berkisar dari {rfm['Recency'].min():.2f} hingga {rfm['Recency'].max():.2f} jam.
    - Frequency: Nilai berkisar dari {rfm['Frequency'].min():.0f} hingga {rfm['Frequency'].max():.0f} penyewaan.
    - Monetary: Nilai berkisar dari {rfm['Monetary'].min():.2f} hingga {rfm['Monetary'].max():.2f} total penyewaan sepeda.
    - Skor RFM tertinggi adalah {rfm['RFM_Score'].max():.2f}, menunjukkan jam yang paling berharga.
    - Skor RFM terendah adalah {rfm['RFM_Score'].min():.2f}, yang mungkin memerlukan strategi perbaikan khusus.
    
    Wawasan tambahan:
    - Jam paling berharga adalah {best_hour}:00, dengan Skor RFM {rfm['RFM_Score'].max():.2f}.
    - Jam paling kurang berharga adalah {worst_hour}:00, dengan Skor RFM {rfm['RFM_Score'].min():.2f}.
    - Jam-jam dengan skor RFM tinggi mungkin merupakan target yang baik untuk promosi atau peningkatan ketersediaan layanan.
    - Jam-jam dengan skor RFM rendah mungkin memerlukan strategi untuk meningkatkan penyewaan sepeda, seperti diskon khusus di luar jam sibuk.
    """)

def time_series_decomposition(filtered_data):
    st.header('5. Time Series Decomposition')
    
    daily_data = filtered_data.set_index('date')['total_count'].resample('D').sum().reset_index()
    daily_data['trend'] = daily_data['total_count'].rolling(window=7, center=True).mean()
    daily_data['seasonal'] = daily_data['total_count'] - daily_data['trend']
    daily_data['residual'] = daily_data['total_count'] - daily_data['trend'] - daily_data['seasonal']
    
    charts = [
        alt.Chart(daily_data).mark_line().encode(x='date', y='total_count', color=alt.value('blue')).properties(width=600, height=200, title='Original Time Series'),
        alt.Chart(daily_data).mark_line().encode(x='date', y='trend', color=alt.value('red')).properties(width=600, height=200, title='Trend'),
        alt.Chart(daily_data).mark_line().encode(x='date', y='seasonal', color=alt.value('green')).properties(width=600, height=200, title='Seasonal'),
        alt.Chart(daily_data).mark_line().encode(x='date', y='residual', color=alt.value('purple')).properties(width=600, height=200, title='Residual')
    ]
    
    st.altair_chart(alt.vconcat(*charts))
    
    trend_direction = 'peningkatan' if daily_data['trend'].iloc[-1] > daily_data['trend'].iloc[0] else 'penurunan'
    seasonal_pattern = 'harian' if len(daily_data) > 7 else 'mingguan'
    
    st.write(f"""
    Analisis dekomposisi time series menunjukkan:
    - Tren: Terlihat adanya {trend_direction} umum dalam jumlah peminjaman sepeda selama periode yang dipilih.
    - Musiman: Pola musiman menunjukkan fluktuasi {seasonal_pattern} dalam peminjaman sepeda.
    - Residual: Komponen residual menangkap variasi yang tidak dapat dijelaskan oleh tren atau musiman, yang mungkin disebabkan oleh faktor-faktor eksternal atau acak.
    """)
def clustering_analysis(filtered_data):
    st.header('6. Simple Clustering')
    
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
    
    best_cluster = cluster_data.loc[cluster_data['total_count'].idxmax()]
    worst_cluster = cluster_data.loc[cluster_data['total_count'].idxmin()]
    
    st.write(f"""
    Analisis clustering sederhana menunjukkan:
    - Kondisi terbaik untuk penyewaan sepeda: {best_cluster['temp_bin']} dan {best_cluster['humidity_bin']}, dengan rata-rata {best_cluster['total_count']:.2f} penyewaan.
    - Kondisi terburuk untuk penyewaan sepeda: {worst_cluster['temp_bin']} dan {worst_cluster['humidity_bin']}, dengan rata-rata {worst_cluster['total_count']:.2f} penyewaan.
    - Perbedaan antara kondisi terbaik dan terburuk adalah {best_cluster['total_count'] - worst_cluster['total_count']:.2f} penyewaan.
    """)

def correlation_analysis(filtered_data):
    st.header('7. Correlation Analysis')
    
    corr_features = ['temperature', 'feels_like_temperature', 'humidity', 'windspeed', 'total_count']
    corr_matrix = filtered_data[corr_features].corr()
    
    corr_heatmap = alt.Chart(corr_matrix.reset_index().melt('index')).mark_rect().encode(
        x='index:O',
        y='variable:O',
        color='value:Q',
        tooltip=['index', 'variable', 'value']
    ).properties(
        width=500,
        height=400,
        title='Correlation Heatmap of Weather Factors and Bike Rentals'
    )
    
    st.altair_chart(corr_heatmap, use_container_width=True)
    
    st.write(f"""
    Analisis korelasi menunjukkan:
    - Korelasi tertinggi dengan jumlah penyewaan sepeda: {corr_matrix['total_count'].abs().sort_values(ascending=False).index[1]} ({corr_matrix['total_count'][corr_matrix['total_count'].abs().sort_values(ascending=False).index[1]]:.2f})
    - Korelasi terendah dengan jumlah penyewaan sepeda: {corr_matrix['total_count'].abs().sort_values().index[0]} ({corr_matrix['total_count'][corr_matrix['total_count'].abs().sort_values().index[0]]:.2f})
    - Suhu dan suhu yang dirasakan memiliki korelasi yang kuat ({corr_matrix['temperature']['feels_like_temperature']:.2f}), menunjukkan kemungkinan multikolinearitas.
    """)

def conclusion_and_recommendations():
    st.header('8. Kesimpulan dan Rekomendasi')
    
    st.write("""
    Berdasarkan analisis yang telah dilakukan, berikut adalah beberapa kesimpulan dan rekomendasi:
    
    1. Cuaca memiliki pengaruh signifikan terhadap jumlah penyewaan sepeda. Cuaca cerah cenderung menghasilkan penyewaan tertinggi.
       Rekomendasi: Meningkatkan ketersediaan sepeda dan staf pada hari-hari dengan prakiraan cuaca baik.
    
    2. Terdapat perbedaan pola penyewaan antara hari kerja dan hari libur.
       Rekomendasi: Menyesuaikan strategi pemasaran dan ketersediaan sepeda berdasarkan jenis hari.
    
    3. Analisis RFM menunjukkan jam-jam tertentu yang lebih berharga.
       Rekomendasi: Fokus pada peningkatan layanan dan promosi khusus selama jam-jam puncak.
    
    4. Tren musiman terlihat jelas dalam data.
       Rekomendasi: Merencanakan inventaris dan pemeliharaan sepeda berdasarkan pola musiman.
    
    5. Suhu dan kelembaban memiliki pengaruh terhadap jumlah penyewaan.
       Rekomendasi: Mempertimbangkan faktor cuaca dalam peramalan permintaan dan perencanaan operasional.
    
    6. Korelasi kuat antara faktor cuaca tertentu dan jumlah penyewaan.
       Rekomendasi: Menggunakan informasi cuaca untuk memprediksi permintaan dan mengoptimalkan alokasi sumber daya.
    
    Implementasi rekomendasi ini diharapkan dapat meningkatkan efisiensi operasional dan kepuasan pelanggan dalam sistem penyewaan sepeda.
    """)

if __name__ == "__main__":
    main()
