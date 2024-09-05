import streamlit as st
import pandas as pd
import requests
import replicate

# Helper function to fetch weather data from OpenWeather API
def get_weather_data(api_key, location):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"cod": response.status_code, "message": response.text}

# Helper function to process weather data
def process_weather_data(data):
    weather_list = data['list']
    processed_data = []
    for weather in weather_list:
        processed_data.append({
            "date": pd.to_datetime(weather['dt_txt']).date(),
            "datetime": pd.to_datetime(weather['dt_txt']),
            "temp": weather['main']['temp'],
            "humidity": weather['main']['humidity'],
            "weather": weather['weather'][0]['description']
        })
    df = pd.DataFrame(processed_data)
    return df

# Function to generate a readable weather summary
def generate_weather_summary(df):
    summary = []
    for _, row in df.iterrows():
        summary.append(f"- **Date**: {row['date']} | **Temp**: {row['temp']}°C | **Humidity**: {row['humidity']}% | **Weather**: {row['weather']}")
    return "\n".join(summary)

# Function to generate AI recommendations based on the weather summary
def generate_recommendations(df, client):
    model = "meta/meta-llama-3-8b-instruct"
    summary = generate_weather_summary(df)  # Generate formatted weather summary

    input_data = {
        "prompt": f"Based on the following weather data, provide recommendations:\n{summary}",
        "max_new_tokens": 512,
    }

    recommendations = []
    try:
        for event in client.stream(model, input=input_data):
            if hasattr(event, 'text'):
                recommendations.append(event.text.strip())  # Append text from each event
    except replicate.exceptions.ReplicateError as e:
        st.error(f"❌ Error: {e}")

    return "\n\n".join(recommendations)  # Return formatted recommendations

# Main Streamlit app logic
def main():
    st.title("Weather Forecast & AI Recommendations 🌦️")
    
    api_key = "53a8b377d161be08079ec9d785a4e968"  # API key for OpenWeather
    replicate_api_key = st.secrets["api_key"]  # API key for Replicate
    
    # Location input
    location = st.text_input("Enter a location to get weather forecast", "London")
    
    if location:
        data = get_weather_data(api_key, location)
        if data and data.get('cod') == '200':
            df = process_weather_data(data)
            
            # Filter the next 5 days weather forecast
            next_5_days = pd.Timestamp.now() + pd.DateOffset(days=5)
            df = df[df['datetime'] <= next_5_days]
            
            # Display weather data summary
            st.subheader("Weather Data Summary (Next 5 Days)")
            weather_summary = generate_weather_summary(df)
            st.markdown(weather_summary)
            
            # Generate and display AI recommendations using the summary
            client = replicate.Client(api_token=replicate_api_key)
            with st.spinner('Generating AI Recommendations...'):
                recommendations = generate_recommendations(df, client)

            st.subheader("🧠 AI Recommendations for Today")
            st.markdown(recommendations)

        else:
            st.error(f"❌ Error: {data.get('message', 'Location not found!')}")

if __name__ == "__main__":
    main()
