import streamlit as st
import requests
import pandas as pd
import altair as alt
from gpt4all import GPT4All

# Function to fetch weather data
def get_weather_data(api_key, location):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Function to process weather data
def process_weather_data(data):
    weather_list = data['list']
    weather_data = []
    for entry in weather_list:
        weather_data.append({
            "datetime": pd.to_datetime(entry['dt_txt']),
            "date": pd.to_datetime(entry['dt_txt']).date(),
            "temp": entry['main']['temp'],
            "humidity": entry['main']['humidity'],
            "weather": entry['weather'][0]['description']
        })
    df = pd.DataFrame(weather_data)
    return df

# Function to generate recommendations for the current day using GPT-4All
def generate_recommendations(df, gpt4all_model_path):
    model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf", model_path=gpt4all_model_path)
    recommendations = []
    with model.chat_session():
        summary = df[['date', 'temp', 'humidity', 'weather']].to_string(index=False)
        prompt = f"Based on the following weather data, provide recommendations:\n{summary}"
        response = model.generate(prompt, max_tokens=1024)
        recommendations.append(f"🌟 {response}")
    return recommendations

# Streamlit app
st.set_page_config(page_title="Weather Insights", page_icon="🌤️", layout="wide")

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    .main .block-container {
        max-width: 1200px;
        padding: 1rem;
    }
    @media (max-width: 600px) {
        .main .block-container {
            padding: 0.5rem;
        }
        .stDataFrame {
            overflow-x: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Insights")
st.markdown("### Get detailed weather statistics, including temperature trends, humidity levels, and weather descriptions for the next 5 days. 🌦️🌡️💧")

location = st.text_input("Enter a location:", "Lagos,ng")
st.markdown("*(Default location is Lagos, Nigeria. You can edit the location above.)*")
api_key = st.secrets["openweather_api_key"]  # Use Streamlit secrets management
gpt4all_model_path = "C:/Users/USER/Downloads/Documents"  # Replace with your actual GPT-4All model path

if location:
    data = get_weather_data(api_key, location)
    if data.get('cod') != '200':
        st.error(f"❌ Error: {data.get('message', 'Location not found!')}")
    else:
        df = process_weather_data(data)
        
        next_5_days = pd.Timestamp.now() + pd.DateOffset(days=5)
        df = df[df['datetime'] <= next_5_days]
        
        current_day = pd.Timestamp.now().date()
        df_current_day = df[df['date'] == current_day]

        # Debugging: Check if df_current_day has data
        st.write("Current Day DataFrame:", df_current_day)

        styled_df = df.style.set_properties(**{
            'background-color': 'lavender',
            'color': 'black',
            'border-color': 'white'
        }).highlight_max(subset=['temp', 'humidity'], color='lightcoral').highlight_min(subset=['temp', 'humidity'], color='lightblue')

        st.write(f"📅 Weather data for {location} (Next 5 Days)")
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

        with st.spinner('Generating A.I Recommendations...'):
            recommendations = generate_recommendations(df_current_day, gpt4all_model_path)

        for i, rec in enumerate(recommendations):
            st.subheader(f"🧠 A.I Recommendations for Today")
            st.markdown(rec)
