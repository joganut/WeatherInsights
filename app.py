import streamlit as st
import requests
import pandas as pd
import altair as alt
import replicate

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

# Function to generate recommendations for the current day using Replicate
def generate_recommendations(df, client):
    model = "meta/meta-llama-3-8b-instruct"
    summary = df[['date', 'temp', 'humidity', 'weather']].to_string(index=False)
    st.write("Summary for recommendations:", summary)  # Debug statement
    input_data = {
        "prompt": f"Based on the following weather data, provide recommendations. categories like what to wear and more:\n{summary}",
        "max_new_tokens": 512,
        "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    }
    recommendations = []
    try:
        for event in client.stream(model, input=input_data):
            st.write("Event received:", event)  # Debug statement
            if hasattr(event, 'text'):
                recommendations.append(event.text)  # Extract the text content
    except replicate.exceptions.ReplicateError as e:
        st.error(f"❌ Error: {e}")
    return " ".join(recommendations)

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
st.markdown("### Get detailed AI recommendations, weather statistics, including temperature trends, humidity levels, and weather descriptions for the next 5 days. 🌦️🌡️💧")

location = st.text_input("Enter a location:", "Lagos,ng")
st.markdown("*(Default location is Lagos, Nigeria. You can edit the location above.)*")
api_key = "53a8b377d161be08079ec9d785a4e968"

if location:
    data = get_weather_data(api_key, location)
    if data.get('cod') != '200':
        st.error(f"❌ Error: {data.get('message', 'Location not found!')}")
    else:
        df = process_weather_data(data)
        
        next_5_days = pd.Timestamp.now() + pd.DateOffset(days=5)
        df = df[df['datetime'] <= next_5_days]

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

        # Initialize the Replicate client with your API token from secrets
        client = replicate.Client(api_token=st.secrets["api_key"])

        with st.spinner('Generating A.I Recommendations...'):
            recommendations = generate_recommendations(df, client)

        st.subheader("🧠 A.I Recommendations for Today")
        st.markdown(recommendations)
