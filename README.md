# Bike Sharing Analysis Dashboard ✨

## Setup environment

```
pip install numpy pandas scipy matplotlib seaborn jupyter streamlit altair
```

## Run Streamlit app

```
streamlit run dashboard/dashboard.py
```

## Project Overview

This project analyzes bike-sharing data to understand the factors influencing bike rentals. The analysis focuses on several key aspects:

1. How does weather affect the number of bike rentals?
2. Is there a significant difference in bike rentals between working days and holidays?
3. What are the temporal patterns in bike rentals?
4. How do temperature and humidity interact to influence bike rentals?
5. What insights can be gained from RFM analysis?
6. What pattern can be observed from time series decomposition?

## File Structure

- `dashboard/`
  - `main_data.csv`: The main dataset used for analysis
  - `dashboard.py`: Streamlit dashboard script
- `data/`
  - `hour.csv`: The dataset used for analysis
  - `day.csv`: The dataset used for analysis
- `README.md`: This file
- `requirements.txt`: List of required Python packages

## Data Analysis Process

1. Data Loading: The dataset (main_data.csv) is loaded using pandas.
2. Data Preprocessing:
   - Convert date to datetime
   - Map weather situations and working days to descriptive labels
   - Convert temperature to Celsius
   - Convert humidity to percentage
3. Exploratory Data Analysis (EDA):
   - Analyzed the impact of weather on bike rentals
   - Compared bike rentals on working days vs. holidays
   - Performed time series decomposition
   - Conducted simple clustering based on temperature and humidity

## Dashboard Components

The Streamlit dashboard (`dashboard.py`) includes:

1. Weather Impact Analysis:

   - Visualizes the distribution of rental patterns

2. Working Days vs. Holidays:

   - Compares bike rental patterns between working days and holidays

3. Daily Trend Analysis:

   - Shows the trend of bike rentals throughout the day for working days and holidays

4. RFM (Recency, Frequency, Monetary) Analysis:

   - Visualizes the distribution of rental patterns
   - Provides insights into customer segmentation

5. Time Series Decomposition:

   - Breaks down the rental data into trend, seasonal, and residual components
   - Helps identify underlying patterns and anomalies

6. Simple Clustering:

   - Groups rental patterns based on temperature and humidity
   - Visualizes the relationship between weather conditions and rental frequency

7. Raw Data Display:
   - Option to view the filtered dataset used in the analysis

## How to Use the Dashboard

1. Ensure all required packages are installed (see Setup environment)
2. Run the Streamlit app using the command provided above
3. Use the sidebar controls to filter data by:
   - Weather condition
   - Day type (Working Day or Holiday)
   - Date range
4. Explore the visualizations and insights provided in the main content area
5. Adjust filters to see how different conditions affect bike rentals

## Key Features

- Interactive filters for data exploration
- Comprehensive analysis of weather impact on bike rentals
- Comparison of rental patterns between working days and holidays
- Daily trend analysis
- RFM analysis for customer segmentation
- Time series decomposition for trend and seasonality analysis
- Simple clustering to visualize weather impacts
- Option to view raw data

## Conclusions

1. Weather Impact:

   - Weather conditions significantly influence bike rental patterns
   - The clustering heatmap provides insights into optimal weather conditions for rentals

2. Working Days vs. Holidays:

   - Rental patterns differ between working days and holidays
   - This is visible in the RFM analysis and time series decomposition

3. Temporal Patterns:

   - The time series decomposition reveals clear trends and seasonal patterns in bike rentals
   - This can help in predicting future rental demands

4. Temperature and Humidity Interaction:
   - The clustering analysis shows how temperature and humidity jointly affect rental frequencies
   - This information can be valuable for inventory management and marketing strategies

## Additional Notes

- The raw data can be displayed by checking the 'Show Raw Data' box in the dashboard
- The dashboard is designed to handle empty filter conditions, displaying a warning when no data matches the selected filters
- For best performance, ensure your dataset (main_data.csv) is up-to-date and correctly formatted

## Future Improvements

- Implement predictive modeling for rental forecasting
- Add more advanced clustering techniques
- Incorporate external data sources (e.g., local events, public transportation schedules)
- Enhance visualization interactivity

## License

This project is licensed under the MIT License.
