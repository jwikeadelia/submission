import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

all_df = pd.read_csv("all_data.csv")
hour_df = pd.read_csv("../data/hour.csv")
day_df = pd.read_csv("../data/day.csv")

day_df['dteday'] = pd.to_datetime(day_df['dteday'])

def process_season_rentals(day_df, hour_df):
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    season_rental_day = day_df.groupby('season')['cnt'].sum().reset_index()

    hour_df['date'] = hour_df['dteday'].dt.date

    daily_rentals_hour = hour_df.groupby('date')['cnt'].sum().reset_index()

    daily_rentals_hour['dteday'] = pd.to_datetime(daily_rentals_hour['date'])

    daily_rentals_hour = daily_rentals_hour.merge(day_df[['dteday', 'season']], on='dteday', how='left')

    season_rental_hour = daily_rentals_hour.groupby('season')['cnt'].sum().reset_index()

    season_rental_total = pd.merge(season_rental_day, season_rental_hour, on='season', suffixes=('_day', '_hour'))

    season_rental_total['total_rentals'] = season_rental_total['cnt_day'] + season_rental_total['cnt_hour']

    season_rental_total['season'] = season_rental_total['season'].replace({
        1: 'spring',
        2: 'summer',
        3: 'fall',
        4: 'winter'
    })

    season_rental_total = season_rental_total.sort_values(by='total_rentals', ascending=False)

    return season_rental_total

def perform_rfm_analysis(day_df):
    analysis_date = day_df['dteday'].max()

    day_df['Recency'] = (analysis_date - day_df['dteday']).dt.days
    day_df['Frequency'] = 1
    day_df['Monetary'] = day_df['cnt']

    rfm_df = day_df.groupby('dteday').agg({
        'Recency': 'min',
        'Frequency': 'sum',
        'Monetary': 'sum'
    }).reset_index()

    rfm_df['R_rank'] = pd.qcut(rfm_df['Recency'], 4, labels=False)
    
    rfm_df['F_rank'] = 1

    if rfm_df['Monetary'].nunique() > 1:
        rfm_df['M_rank'] = pd.qcut(rfm_df['Monetary'], 4, labels=False)
    else:
        rfm_df['M_rank'] = 1

    rfm_df['RFM_Score'] = rfm_df['R_rank'].astype(str) + rfm_df['F_rank'].astype(str) + rfm_df['M_rank'].astype(str)

    return rfm_df[['dteday', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']]


min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

st.sidebar.header("Filter Rentang Waktu")

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

filtered_data = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & 
                       (day_df['dteday'] <= pd.to_datetime(end_date))]

total_cnt = filtered_data['cnt'].sum()

st.header('Bike Rental Dashboard :bike:')

st.subheader('Peak Bike Rentals By Hour')
rentals_by_hour = hour_df.groupby('hr')['cnt'].sum().reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(x='hr', y='cnt', data=rentals_by_hour, palette='Blues')

plt.xlabel('Hour', fontsize=12)
plt.ylabel('Rental Amount', fontsize=12)

st.pyplot(plt)

st.subheader('Bicycle Rental Comparison Between Seasons')

season_rentals = process_season_rentals(day_df, hour_df)

plt.figure(figsize=(10, 6))
sns.barplot(x='season', y='total_rentals', data=season_rentals, palette='Blues')

plt.xlabel('Season', fontsize=14)
plt.ylabel('Total Rental', fontsize=14)

st.pyplot(plt)

st.subheader('Bicycle Rental Behavior Review Based on RFM Parameters')

rfm_df = perform_rfm_analysis(day_df)

fig, ax = plt.subplots(1, 3, figsize=(21, 9))

sns.histplot(rfm_df['Recency'], bins=20, kde=True, ax=ax[0], color='skyblue')
ax[0].set_title('Distribusi Recency (R)', fontsize=20)
ax[0].set_xlabel('Recency', fontsize=18)
ax[0].set_ylabel('instant', fontsize=18)

sns.histplot(rfm_df['Frequency'], bins=20, kde=True, ax=ax[1], color='skyblue')
ax[1].set_title('Distribusi Frequency (F)', fontsize=20)
ax[1].set_xlabel('Frequency', fontsize=18)
ax[1].set_ylabel('instant', fontsize=18)

sns.histplot(rfm_df['Monetary'], bins=20, kde=True, ax=ax[2], color='skyblue')
ax[2].set_title('Distribusi Monetary (M)', fontsize=20)
ax[2].set_xlabel('Monetary', fontsize=18)
ax[2].set_ylabel('instant', fontsize=18)

plt.tight_layout()
st.pyplot(plt)

st.subheader('Monthly Bike Rental Trends')

st.subheader(f'Total Bike Rentals from {start_date} to {end_date}')
st.metric(label="Total Bike Rentals", value=total_cnt)


day_df['dteday'] = pd.to_datetime(day_df['dteday'])

day_df.set_index('dteday', inplace=True)

monthly_orders_df = day_df.resample('M').agg({'cnt': 'sum'}).reset_index()

plt.figure(figsize=(10, 6))
plt.plot(monthly_orders_df['dteday'], monthly_orders_df['cnt'], marker='o', color='b', linestyle='-', label='Total Bike Rental')

plt.xlabel('Month', fontsize=12)
plt.ylabel('Rental Amount', fontsize=12)
plt.grid(True)
plt.xticks(rotation=45)

plt.legend()
st.pyplot(plt)

st.caption('Copyright (c) Dicoding 2023')