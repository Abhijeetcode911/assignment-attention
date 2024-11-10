# # main.py
# from fastapi import FastAPI, Request
# from neo4j import GraphDatabase
# from pydantic import BaseModel
# import requests
# import json
# app = FastAPI()

# # Initialize Neo4j driver
# neo4j_driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "attention.ai"))

# # Ollama model settings
# OLLAMA_MODEL = "llama2"  # Replace with the specific Ollama model you're using

# # Data model for user preferences
# class UserPreference(BaseModel):
#     city: str
#     start_time: str
#     end_time: str
#     interests: list
#     budget: int

# # Utility function to generate text using Ollama
# def generate_text(prompt):
#     try:
#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={"model": OLLAMA_MODEL, "prompt": prompt},
#             stream=True  # Enable streaming response
#         )
#         response.raise_for_status()

#         # Accumulate the full response
#         full_response = ""
#         for line in response.iter_lines():
#             if line:
#                 # Each line is a JSON object; parse it
#                 line_data = line.decode('utf-8')
#                 data = json.loads(line_data)
                
#                 # Append the partial response
#                 full_response += data.get("response", "")

#                 # Check if the stream has completed
#                 if data.get("done", False):
#                     break

#         return full_response if full_response else "Error: No response generated."
#     except requests.exceptions.RequestException as e:
#         return f"Request failed: {e}"
#     except json.JSONDecodeError as e:
#         return f"JSON parsing error: {e}"


# # API endpoint to collect preferences
# @app.post("/collect_preferences/")
# async def collect_preferences(preferences: UserPreference):
#     with neo4j_driver.session() as session:
#         session.run("""
#             CREATE (u:User {city: $city, start_time: $start_time, end_time: $end_time,
#             interests: $interests, budget: $budget})
#             """, city=preferences.city, start_time=preferences.start_time,
#             end_time=preferences.end_time, interests=preferences.interests, budget=preferences.budget)
#     return {"status": "Preferences collected successfully"}

# # API endpoint to generate itinerary
# @app.post("/generate_itinerary/")
# async def generate_itinerary(preferences: UserPreference):
#     prompt = f"Create a one-day itinerary for {preferences.city} with interests {preferences.interests}."
#     response = generate_text(prompt)
#     return {"itinerary": response}



from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from pydantic import BaseModel
import os
import requests
import json
import re
from datetime import datetime

app = FastAPI()

# Environment variables for API keys
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Neo4j driver initialization
neo4j_driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "attention.ai"))

# Ollama model settings
OLLAMA_MODEL = "llama2"

class UserPreference(BaseModel):
    user_id: str
    city: str
    start_time: str
    end_time: str
    interests: list
    budget: int
    starting_point: str = None

def generate_text(prompt):
    """Generates response from LLM model with structured schema for itinerary details."""
    schema = """
    Please provide the itinerary in the following structured format. Each stop should include a location name and any necessary address or details for accurate mapping. 

    Format:
    1. Stop Name: [Name of the Stop, e.g., "Eiffel Tower, Paris" or "Central Park, New York"]
       - Address: [Full address or location description if available, e.g., "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"]
       - Time: [Start Time] - [End Time]
       - Activity: [Brief description of the activity]
       - Travel Method: [Mode of travel, e.g., taxi, walk, subway]
       - Travel Time: [Approximate travel time, e.g., "15 minutes"]
       - Cost: [Cost in local currency, if applicable]
       - Additional Notes: [Any additional information, e.g., "pre-booking required"]

    Example:
    1. Stop Name: Eiffel Tower, Paris
       - Address: Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France
       - Time: 9:00 AM - 10:30 AM
       - Activity: Visit and explore the Eiffel Tower.
       - Travel Method: Taxi
       - Travel Time: 15 minutes
       - Cost: 25 Euros
       - Additional Notes: You can go up the tower for an additional fee.

    Continue in this format for all stops in the itinerary.
    Include a final line with "Total Estimated Cost: [Total cost for the day]" if applicable.
    """

    full_prompt = prompt + "\n\n" + schema
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": full_prompt},
            stream=True
        )
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_data = line.decode('utf-8')
                data = json.loads(line_data)
                full_response += data.get("response", "")
                if data.get("done", False):
                    break
        return full_response if full_response else "Error: No response generated."
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e}"

def store_user_memory(user_id, preferences):
    """Stores user preferences in Neo4j for continuity across sessions."""
    with neo4j_driver.session() as session:
        interests_str = ', '.join(preferences['interests']) if preferences.get('interests') else ""
        session.run("""
            MERGE (u:User {id: $user_id})
            SET u.city = $city,
                u.start_time = $start_time,
                u.end_time = $end_time,
                u.interests = $interests,
                u.budget = $budget,
                u.starting_point = $starting_point
            """, user_id=user_id, city=preferences.get('city'), start_time=preferences.get('start_time'),
            end_time=preferences.get('end_time'), interests=interests_str,
            budget=preferences.get('budget'), starting_point=preferences.get('starting_point'))

def get_recommendations_based_on_city(city):
    """Fetch popular places in a city using Google Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=popular+places+in+{city}&key={GOOGLE_PLACES_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [place["name"] for place in data["results"][:5]]
    except requests.RequestException as e:
        print(f"Error fetching recommendations for {city}: {e}")
        return ["Local landmarks", "Museums", "Food markets"]

@app.get("/fetch_weather/{city}")
async def fetch_weather(city: str):
    """Fetch weather data for the city using OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_info = {
            "forecast": data["weather"][0]["description"].capitalize(),
            "temperature": f"{data['main']['temp']} °C",
            "advice": "Ideal for outdoor activities." if data["main"]["temp"] > 15 else "Consider wearing a jacket."
        }
        return weather_info
    except requests.RequestException as e:
        print(f"Error fetching weather for {city}: {e}")
        return {"forecast": "Weather data unavailable", "advice": "Check the local weather."}

def get_coordinates(place_name, city, address=None):
    """Fetch coordinates for a given place using Nominatim API with a retry mechanism."""
    query_attempts = [
        address,                  # Most specific: full address
        f"{place_name}, {city}",  # Fallback: place name + city
        city                      # Least specific: city only
    ]
    
    for query in query_attempts:
        if not query:  # Skip if query is None
            continue
        
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "tour-planning-app"}
            )
            response.raise_for_status()
            data = response.json()
            
            if data:  # If valid coordinates are found, return them
                print(f"Coordinates found for '{query}': ({data[0]['lat']}, {data[0]['lon']})")
                return float(data[0]["lat"]), float(data[0]["lon"])
            else:
                print(f"Warning: No coordinates found for query '{query}'.")

        except requests.RequestException as e:
            print(f"Error fetching coordinates for query '{query}': {e}")
    
    # If all attempts fail, return a placeholder indicating failure
    print("All attempts failed to fetch coordinates.")
    return (None, None)

@app.post("/collect_preferences/")
async def collect_preferences(preferences: UserPreference):
    """Collect user preferences and store them in Neo4j."""
    preference_data = preferences.dict()
    try:
        store_user_memory(preferences.user_id, preference_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing preferences: {e}")

    if not preferences.interests:
        recommendations = get_recommendations_based_on_city(preferences.city)
        return {
            "status": "Preferences collected successfully",
            "recommendations": recommendations
        }
    return {"status": "Preferences collected successfully"}

@app.post("/generate_itinerary/")
async def generate_itinerary(preferences: UserPreference):
    """Generate a detailed itinerary with structured stops and map data."""
    prompt = (
        f"Create a detailed itinerary for {preferences.city} that includes activities related "
        f"to {preferences.interests}, starting from {preferences.starting_point or 'a central location'} "
        f"at {preferences.start_time} and ending by {preferences.end_time}. "
        f"Budget is approximately {preferences.budget}. Format the response as per the provided schema."
    )
    
    response = generate_text(prompt)
    print("Debug - Raw LLM Response:", response)

    stops = extract_stops_from_response(response)
    print("Debug - Extracted Stops:", stops)

    map_data = []
    for stop in stops:
        coordinates = get_coordinates(stop["name"], preferences.city, stop.get("address"))
        
        # Only include stops with valid coordinates
        if coordinates != (None, None):
            map_data.append({
                "place": stop["name"],
                "coordinates": coordinates,
                "address": stop["address"],
                "start_time": stop["start_time"],
                "end_time": stop["end_time"],
                "activity": stop["activity"],
                "travel_method": stop["travel_method"],
                "cost": stop["cost"]
            })
        else:
            print(f"Skipping stop '{stop['name']}' due to failed geocoding.")

    itinerary = format_itinerary(response)
    return {"itinerary": itinerary, "map_data": map_data}

def extract_stops_from_response(response_text):
    """Extracts stops with detailed location info from the LLM-generated response text."""
    stop_pattern = re.compile(
        r"\d+\.\s*Stop Name:\s*(.+?)\n\s*- Address:\s*(.+?)\n\s*- Time:\s*(\d{1,2}:\d{2} [AP]M)\s*-\s*(\d{1,2}:\d{2} [AP]M)\n\s*- Activity:\s*(.+?)\n\s*- Travel Method:\s*(.+?)\n\s*- Travel Time:\s*(\d+ minutes)\n\s*- Cost:\s*([^\n]*)",
        re.DOTALL
    )
    
    stops = []
    for match in stop_pattern.finditer(response_text):
        stop = {
            "name": match.group(1),
            "address": match.group(2),
            "start_time": match.group(3),
            "end_time": match.group(4),
            "activity": match.group(5),
            "travel_method": match.group(6),
            "travel_time": match.group(7),
            "cost": match.group(8)
        }
        stops.append(stop)

    return stops

def format_itinerary(raw_text):
    formatted_text = f"{raw_text}\n\nWeather Recommendation: Ideal for outdoor activities."
    return formatted_text


# from fastapi import FastAPI, HTTPException
# from neo4j import GraphDatabase
# from pydantic import BaseModel
# import requests
# import json
# from datetime import datetime

# app = FastAPI()

# # Initialize Neo4j driver
# neo4j_driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "attention.ai"))

# # Ollama model settings
# OLLAMA_MODEL = "llama2"

# class UserPreference(BaseModel):
#     user_id: str
#     city: str
#     start_time: str
#     end_time: str
#     interests: list
#     budget: int
#     starting_point: str = None

# def generate_text(prompt):
#     """Function to generate response from LLM model"""
#     try:
#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={"model": OLLAMA_MODEL, "prompt": prompt},
#             stream=True
#         )
#         response.raise_for_status()
#         full_response = ""
#         for line in response.iter_lines():
#             if line:
#                 line_data = line.decode('utf-8')
#                 data = json.loads(line_data)
#                 full_response += data.get("response", "")
#                 if data.get("done", False):
#                     break
#         return full_response if full_response else "Error: No response generated."
#     except requests.exceptions.RequestException as e:
#         return f"Request failed: {e}"
#     except json.JSONDecodeError as e:
#         return f"JSON parsing error: {e}"

# def store_user_memory(user_id, preferences):
#     """Stores user preferences in Neo4j for continuity across sessions."""
#     with neo4j_driver.session() as session:
#         # Convert interests to a comma-separated string
#         interests_str = ', '.join(preferences['interests']) if preferences.get('interests') else ""

#         # Run query with each property separately
#         session.run("""
#             MERGE (u:User {id: $user_id})
#             SET u.city = $city,
#                 u.start_time = $start_time,
#                 u.end_time = $end_time,
#                 u.interests = $interests,
#                 u.budget = $budget,
#                 u.starting_point = $starting_point
#             """, user_id=user_id, city=preferences.get('city'), start_time=preferences.get('start_time'),
#             end_time=preferences.get('end_time'), interests=interests_str,
#             budget=preferences.get('budget'), starting_point=preferences.get('starting_point'))

# @app.post("/collect_preferences/")
# async def collect_preferences(preferences: UserPreference):
#     """Collect user preferences and store them in Neo4j for future personalization."""
#     preference_data = preferences.dict()
#     try:
#         store_user_memory(preferences.user_id, preference_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error storing preferences: {e}")

#     if not preferences.interests:
#         recommendations = get_recommendations_based_on_city(preferences.city)
#         return {
#             "status": "Preferences collected successfully",
#             "recommendations": recommendations
#         }
#     return {"status": "Preferences collected successfully"}

# def get_recommendations_based_on_city(city):
#     """Mock function for city-based recommendations if user is unsure of interests."""
#     popular_sites = {
#         "Rome": ["Colosseum", "Roman Forum", "Pantheon"],
#         "New York": ["Statue of Liberty", "Central Park", "Brooklyn Bridge"]
#     }
#     return popular_sites.get(city, ["Local landmarks", "Museums", "Food markets"])

# @app.post("/generate_itinerary/")
# async def generate_itinerary(preferences: UserPreference):
#     prompt = (
#         f"Create a detailed itinerary for {preferences.city} that includes activities related "
#         f"to {preferences.interests}, starting from {preferences.starting_point or 'a central location'} "
#         f"at {preferences.start_time} and ending by {preferences.end_time}. "
#         f"Budget is approximately {preferences.budget}. Provide clear times, travel methods, "
#         f"and approximate costs. Format the response with each stop as a structured list."
#     )
#     response = generate_text(prompt)

#     stops = extract_stops_from_response(response)
#     optimized_stops = optimize_stops_based_on_budget(stops, preferences.budget)
#     map_url = construct_map_url(optimized_stops)
#     itinerary = format_itinerary(response, map_url)
#     return itinerary

# def extract_stops_from_response(response_text):
#     """Mock function to extract stops from response text for map generation."""
#     stops = ["Colosseum", "Roman Forum", "Pantheon", "Trevi Fountain"]  # Example stops
#     return stops

# def optimize_stops_based_on_budget(stops, budget):
#     """Optimize stops based on user budget."""
#     return stops[:4] if budget < 100 else stops

# def construct_map_url(stops):
#     """Generate a Google Maps URL with all itinerary stops."""
#     base_url = "https://www.google.com/maps/dir/?api=1"
#     waypoints = "&waypoints=" + "|".join(stops[1:-1]) if len(stops) > 2 else ""
#     map_url = f"{base_url}&origin={stops[0]}&destination={stops[-1]}{waypoints}"
#     return map_url

# def format_itinerary(raw_text, map_url):
#     """Format itinerary with details and interactive map link."""
#     formatted_text = f"{raw_text}\n\nWeather Recommendation: Ideal for outdoor activities."
#     formatted_text += f"\n\nInteractive Map: [View on Google Maps]({map_url})"
#     return {"itinerary": formatted_text}

# @app.get("/fetch_weather/{city}")
# async def fetch_weather(city: str):
#     """Fetch weather data and offer recommendations based on forecast."""
#     weather_info = {
#         "forecast": "Sunny with mild temperatures",
#         "advice": "Great for outdoor activities, pack comfortable shoes and water."
#     }
#     return weather_info

# @app.get("/check_attraction_status/{attraction}")
# async def check_attraction_status(attraction: str):
#     """Fetches the open/close status of an attraction."""
#     mock_status = {"status": "Open", "hours": "9:00 AM - 5:00 PM"}
#     return mock_status
