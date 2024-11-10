
# One-Day Tour Planning Assistant

Welcome to the **One-Day Tour Planning Assistant**! This app leverages the power of language models to provide customized tour itineraries based on user preferences, including destination city, interests, budget, and available travel time. The application uses a combination of APIs for recommendations and weather forecasts, along with a visual map of itinerary stops using `Streamlit` and `Folium`.

## Features

- **User Preference Collection**: Allows users to specify their preferences, such as city, start and end time, budget, interests, and starting location.
- **Itinerary Generation**: Creates a structured, one-day itinerary using a language model tailored to the user's preferences.
- **Weather Forecast Integration**: Fetches real-time weather information for the destination city to help users plan accordingly.
- **Map Visualization**: Displays itinerary stops on an interactive map with details and travel information between locations.
- **Customizable Tour Stops**: Provides popular place recommendations if users are unsure about their interests.

## Project Structure

```plaintext
project-folder/
├── main.py                 # FastAPI server code for itinerary generation
├── app.py                  # Streamlit application for user interaction
├── requirements.txt        # List of required Python packages
├── README.md               # Project documentation (this file)
└── .env                    # Environment variables for API keys
```

## Dependencies

- **FastAPI**: For the backend API server to handle itinerary generation.
- **Streamlit**: Provides the interactive user interface.
- **Folium**: Used for creating interactive maps with itinerary stops.
- **Neo4j**: Graph database to store user preferences and enable personalized recommendations.
- **Ollama Model**: Used to generate a detailed itinerary from the language model.
- **APIs**:
  - `Google Places API`: Fetches popular places for city-based recommendations.
  - `OpenWeatherMap API`: Retrieves weather forecasts for the selected destination.

## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Abhijeetcode911/assignment-attention.git
   
    ```

2. **Install Required Packages**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Environment Configuration**:
    Create a `.env` file to store API keys for `Google Places API`, `OpenWeatherMap API`, and other environment variables as shown below:
    ```plaintext
    GOOGLE_PLACES_API_KEY=your_google_places_api_key
    OPENWEATHER_API_KEY=your_openweather_api_key
    ```

4. **Run the Backend Server**:
    Start the FastAPI server for handling requests:
    ```bash
    uvicorn main:app --reload
    ```

5. **Run the Streamlit Frontend**:
    Launch the user interface:
    ```bash
    streamlit run app.py
    ```

6. **Access the Application**:
    Open a web browser and go to `http://localhost:8501` to start using the app.

## Usage Guide

1. **Enter Tour Preferences**: Specify your username, city, start and end times, budget, interests, and starting point.
2. **Generate Itinerary**: Click "Plan my Tour" to save your preferences and generate an itinerary.
3. **View Itinerary and Map**: The generated itinerary will display along with an interactive map of the stops.
4. **Weather Forecast**: See weather recommendations for the day’s itinerary.

## Troubleshooting

- **API Key Errors**: Ensure valid API keys are set up in the `.env` file and that they have appropriate access.
- **Backend Server Issues**: Ensure Neo4j and other dependencies are correctly installed and running before launching the FastAPI server.
- **Map Display**: If the map is not displaying correctly, ensure that `folium` and `streamlit_folium` packages are installed and updated.

## Future Improvements

- **Multi-day Itineraries**: Extend functionality to generate itineraries for multiple days.
- **Hotel and Restaurant Recommendations**: Use additional APIs to provide lodging and dining suggestions.
- **Social Sharing**: Allow users to share their itinerary via social media or email.

## License

This project is licensed under the MIT License.
