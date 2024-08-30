# Dicoding Collection Dashboard ✨

## Setup environment

```
pip install numpy pandas scipy matplotlib seaborn jupyter streamlit
```

## Run steamlit app

```
streamlit run dashboard/dashboard.py
```

## Project Overview

This project analyzes bike-sharing data to understand the factors influencing bike rentals. The analysis focuses on two main questions:

1. How does weather affect the number of bike rentals?
2. Is there a significant difference in bike rentals between working days and holidays?

## File Structure

- `dashboard/`
  - `main_data.csv`: The main dataset used for analysis
  - `dashboard.py`: Streamlit dashboard script
- `data/`
  - `hour.csv`: Hourly bike rental data
  - `day.csv`: Daily bike rental data
- `notebook.ipynb`: Jupyter notebook containing the data analysis process
- `README.md`: This file
- `requirements.txt`: List of required Python packages

## Data Analysis Process

1. Data Loading: The datasets (hour.csv and day.csv) are loaded using pandas.
2. Data Cleaning: Checked for missing values and data integrity.
3. Exploratory Data Analysis (EDA):
   - Analyzed the impact of weather on bike rentals
   - Compared bike rentals on working days vs. holidays
4. Visualization: Created various plots to illustrate the findings

## Dashboard Components

The Streamlit dashboard (`dashboard.py`) includes:

1. Weather impact on bike rentals (box plot)
2. Comparison of rentals on working days vs. holidays (box plot)
3. Hourly trend of bike rentals (line plot)

## How to Use the Dashboard

1. Ensure all required packages are installed (see Setup environment)
2. Run the Streamlit app using the command provided above
3. Use the sidebar controls to filter data by weather condition and day type
4. Explore the visualizations and insights provided in the main content area

## Conclusions

1. Weather Impact:

   - Better weather conditions (categories 1 and 2) tend to result in higher bike rentals
   - Worse weather conditions (categories 3 and 4) lead to lower rental numbers

2. Working Days vs. Holidays:

   - Working days tend to have higher and more consistent rental numbers
   - Holidays show greater variation in rental numbers

3. Daily Trend:
   - Two main peaks in rentals: morning (around 8 AM) and evening (around 5-6 PM)
   - This pattern likely reflects commuting habits

## Additional Notes

- The raw data can be displayed by checking the 'Show Raw Data' box in the dashboard
- For more detailed analysis, refer to the `notebook.ipynb` file
