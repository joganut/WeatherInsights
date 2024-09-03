# 🌤️ Weather Insights

Exciting Update: Weather Insights App Now with AI Recommendations! 🌤️

I am thrilled to announce a major update to our Weather Insights app! 🚀

Our app now features AI-powered recommendations to help you make the most of your day, no matter the weather. Whether you’re planning your week, deciding what to wear, or organizing outdoor activities, our AI recommendations have got you covered. 🌦️🌡️💧

Welcome to the Weather Insights app! This Streamlit application provides detailed weather statistics, including temperature trends, humidity levels, and weather descriptions for the next 5 days.

## 🚀 Features

- **Temperature Trends**: Visualize temperature changes over the next 5 days.
- **Humidity Levels**: Track humidity levels with interactive charts.
- **Weather Descriptions**: Get a summary of weather conditions for each day.

## 🛠️ Technologies Used

- **Languages**: Python
- **Frameworks**: Streamlit
- **Data Visualization**: Altair
- **APIs**: OpenWeatherMap

## 📦 Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/weather-insights.git
    cd weather-insights
    ```

2. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the app**:
    ```bash
    streamlit run app.py
    ```

## 🔧 Configuration

1. **API Key**: Obtain an API key from OpenWeatherMap and add it to the `app.py` file:
    ```python
    api_key = "your_api_key_here"
    ```

2. **Default Location**: The default location is set to Lagos, Nigeria. You can change this in the `app.py` file:
    ```python
    location = st.text_input("Enter a location:", "Lagos,ng")
    ```

## 📊 Usage

- **Enter a Location**: Type in the location for which you want to get weather insights.
- **View Data**: The app will display temperature trends, humidity levels, and weather descriptions for the next 5 days.
