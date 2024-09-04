import streamlit as st
import requests
import pandas as pd
import altair as alt

# Function to fetch weather data
def get_weather_data(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily,alerts&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Function to process weather data
def process_weather_data(data):
    hourly_data = data['hourly']
    weather_data = []
    for entry in hourly_data:
        weather_data.append({
            "datetime": pd.to_datetime(entry['dt'], unit='s'),
            "temp": entry['temp'],
            "humidity": entry['humidity'],
            "weather": entry['weather'][0]['description']
        })
    df = pd.DataFrame(weather_data)
    return df

# Streamlit app
st.set_page_config(page_title="Weather Insights", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Insights")
st.markdown("### Get detailed weather statistics, including temperature trends, humidity levels, and weather descriptions for the next 48 hours. 🌦️🌡️💧")

location = st.text_input("Enter a location:", "Lagos,ng")
st.markdown("*(Default location is Lagos, Nigeria. You can edit the location above.)*")
api_key = st.secrets["openweather_api_key"]  # Use Streamlit secrets management

if location:
    # Get latitude and longitude for the location
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"
    geocode_response = requests.get(geocode_url).json()
    if not geocode_response:
        st.error("❌ Error: Location not found!")
    else:
        lat = geocode_response[0]['lat']
        lon = geocode_response[0]['lon']
        
        data = get_weather_data(api_key, lat, lon)
        df = process_weather_data(data)
        
        next_48_hours = pd.Timestamp.now() + pd.DateOffset(hours=48)
        df = df[df['datetime'] <= next_48_hours]

        styled_df = df.style.set_properties(**{
            'background-color': 'lavender',
            'color': 'black',
            'border-color': 'white'
        }).highlight_max(subset=['temp', 'humidity'], color='lightcoral').highlight_min(subset=['temp', 'humidity'], color='lightblue')

        st.write(f"📅 Weather data for {location} (Next 48 Hours)")
        st.dataframe(styled_df)

        st.subheader("🌡️ Temperature Trends")
        temp_chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('datetime:T', title='Date', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('temp:Q', title='Temperature (°C)'),
            tooltip=[alt.Tooltip('datetime:T', title='Date and Time', format='%Y-%m-%d %H:%M'), 'temp:Q']
        ).properties(
            title='Temperature Trends'
        ).configure_mark(
            color='orange'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(temp_chart, use_container_width=True)

        st.subheader("💧 Humidity Levels")
        humidity_chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('datetime:T', title='Date', axis=alt.Axis(format='%Y-%m-%d %H:%M')),
            y=alt.Y('humidity:Q', title='Humidity (%)'),
            tooltip=[alt.Tooltip('datetime:T', title='Date and Time', format='%Y-%m-%d %H:%M'), 'humidity:Q']
        ).properties(
            title='Humidity Levels'
        ).configure_mark(
            color='blue'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(humidity_chart, use_container_width=True)

        st.subheader("🌈 Weather Description")
        weather_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('weather:N', title='Weather Description'),
            y=alt.Y('count():Q', title='Frequency'),
            tooltip=['weather:N', 'count():Q']
        ).properties(
            title='Weather Description Frequency'
        ).configure_mark(
            color='green'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(weather_chart, use_container_width=True)
