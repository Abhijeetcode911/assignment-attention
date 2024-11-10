

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.title("One-Day Tour Planning Assistant")
st.write("Plan a one-day tour tailored to your preferences!")

# User input fields
username = st.text_input("Enter your username to log in")
if username:
    st.write(f"Welcome, {username}!")

city = st.text_input("City to Visit")
start_time = st.text_input("Start Time (e.g., 9:00 AM)")
end_time = st.text_input("End Time (e.g., 6:00 PM)")
budget = st.number_input("Budget", min_value=0)
interests = st.multiselect("Interests", ["Culture", "Adventure", "Food", "Shopping"])
starting_point = st.text_input("Starting Point (e.g., hotel location)")

# Initialize session state variables to persist data
if "itinerary_data" not in st.session_state:
    st.session_state["itinerary_data"] = None
if "map_data" not in st.session_state:
    st.session_state["map_data"] = None

# Handle "Plan my Tour" button click
if st.button("Plan my Tour"):
    try:
        # Collect preferences
        response = requests.post("http://localhost:8000/collect_preferences/", json={
            "user_id": username,
            "city": city,
            "start_time": start_time,
            "end_time": end_time,
            "budget": budget,
            "interests": interests,
            "starting_point": starting_point
        })
        response.raise_for_status()
        st.success("Preferences collected successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error collecting preferences: {e}")
        st.stop()

    # Generate itinerary
    try:
        itinerary_response = requests.post("http://localhost:8000/generate_itinerary/", json={
            "user_id": username,
            "city": city,
            "start_time": start_time,
            "end_time": end_time, 
            "interests": interests,
            "budget": budget,
            "starting_point": starting_point
        })
        itinerary_response.raise_for_status()

        # Store data in session state
        data = itinerary_response.json()
        st.session_state["itinerary_data"] = data.get("itinerary")
        st.session_state["map_data"] = data.get("map_data")

        # Debugging: Display map data to check format
        st.write("Debug - Map Data:", st.session_state["map_data"])

    except requests.exceptions.RequestException as e:
        st.error(f"Error generating itinerary: {e}")
        st.stop()

# Display itinerary data if available
if st.session_state["itinerary_data"]:
    st.write("Generated Itinerary:", st.session_state["itinerary_data"])
else:
    st.error("Failed to generate itinerary. Please try again.")

# Display map if map data is available
if st.session_state["map_data"]:
    st.write("Displaying Map of Itinerary Stops:")
    try:
        center_coords = st.session_state["map_data"][0]["coordinates"]  # Center map on the first location
        itinerary_map = folium.Map(location=center_coords, zoom_start=13)

        for i, stop in enumerate(st.session_state["map_data"]):
            folium.Marker(
                location=stop["coordinates"],
                popup=f"{i+1}. {stop['place']} ({stop['start_time']} - {stop['end_time']})",
                tooltip=stop["activity"]
            ).add_to(itinerary_map)
            if i > 0:
                prev_stop = st.session_state["map_data"][i - 1]
                folium.PolyLine([prev_stop["coordinates"], stop["coordinates"]], color="blue", weight=2.5).add_to(itinerary_map)

        # Display the map using st_folium
        st_folium(itinerary_map, width=700, height=500)

    except Exception as e:
        st.error(f"Error displaying map: {e}")
else:
    st.warning("No map data available to display. Please verify if the itinerary generated correct stops and coordinates.")

st.write("**Chat History**")
st.text_area("Conversations will appear here as the assistant interacts with you.")





















# import streamlit as st
# import requests
# import folium
# from streamlit_folium import st_folium
# from datetime import datetime

# # Set up page with a cute Trippy branding
# st.set_page_config(
#     page_title="Trippy: Your Personalized Travel Companion",
#     page_icon="🧳",
#     layout="centered",
# )

# # Branding and cute styles
# st.markdown("""
#     <style>
#         .title {
#             font-size: 2.5em;
#             font-weight: bold;
#             color: #FF4081;
#             text-align: center;
#             margin-top: 10px;
#         }
#         .subheading {
#             font-size: 1.5em;
#             color: #42A5F5;
#             margin-top: 20px;
#             text-align: center;
#         }
#         .greeting {
#             font-size: 1.1em;
#             color: #2E7D32;
#             text-align: center;
#             margin-bottom: 20px;
#         }
#         .section {
#             margin-top: 30px;
#             padding: 20px;
#             border-radius: 10px;
#             background-color: #FAFAFA;
#             box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
#         }
#         .result-container {
#             padding: 15px;
#             border-radius: 10px;
#             background-color: #FFFFFF;
#             color: black;
#             box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
#             margin-top: 20px;
#         }
#         .map-container {
#             margin-top: 15px;
#             border-radius: 10px;
#             overflow: hidden;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # App title and description
# st.markdown("<div class='title'>🧳 Trippy: Your Personalized Travel Companion 🌏</div>", unsafe_allow_html=True)
# st.write("Trippy is here to make your travel planning simple and fun! Get a custom one-day itinerary based on your preferences with just a few clicks!")

# # Dynamic greeting on entering username
# username = st.text_input("Enter your name")
# if username:
#     st.markdown(f"<div class='greeting'>Welcome to Trippy, {username}! 🎉</div>", unsafe_allow_html=True)

# # Container for user input fields
# st.markdown("<div class='subheading'>Plan Your Trip</div>", unsafe_allow_html=True)
# with st.form("preferences_form"):
#     city = st.text_input("City to Visit", placeholder="e.g., Mumbai, Jaipur")
#     start_time = st.time_input("Start Time", datetime.strptime("09:00 AM", "%I:%M %p").time())
#     end_time = st.time_input("End Time", datetime.strptime("06:00 PM", "%I:%M %p").time())
#     budget = st.number_input("Budget (INR ₹)", min_value=0, step=500)
#     interests = st.multiselect("Interests", ["Culture", "Adventure", "Food", "Shopping"])
#     starting_point = st.text_input("Starting Point (e.g., hotel location)", placeholder="e.g., Hotel Oberoi")

#     submit_button = st.form_submit_button("Plan My Trip")

# # Initialize session state variables to persist data
# if "itinerary_data" not in st.session_state:
#     st.session_state["itinerary_data"] = None
# if "map_data" not in st.session_state:
#     st.session_state["map_data"] = None

# # Handle form submission and data processing
# if submit_button:
#     if not username or not city or not interests:
#         st.warning("Please fill in all required fields: name, city, and at least one interest.")
#     else:
#         try:
#             # Collect preferences
#             response = requests.post("http://localhost:8000/collect_preferences/", json={
#                 "user_id": username,
#                 "city": city,
#                 "start_time": start_time.strftime("%I:%M %p"),
#                 "end_time": end_time.strftime("%I:%M %p"),
#                 "budget": budget,
#                 "interests": interests,
#                 "starting_point": starting_point
#             })
#             response.raise_for_status()
#             st.success("Preferences saved! Generating your itinerary...")

#             # Generate itinerary
#             itinerary_response = requests.post("http://localhost:8000/generate_itinerary/", json={
#                 "user_id": username,
#                 "city": city,
#                 "start_time": start_time.strftime("%I:%M %p"),
#                 "end_time": end_time.strftime("%I:%M %p"),
#                 "interests": interests,
#                 "budget": budget,
#                 "starting_point": starting_point
#             })
#             itinerary_response.raise_for_status()

#             # Store data in session state
#             data = itinerary_response.json()
#             st.session_state["itinerary_data"] = data.get("itinerary")
#             st.session_state["map_data"] = data.get("map_data")

#         except requests.exceptions.RequestException as e:
#             st.error(f"Error: {e}")

# # Display the generated itinerary if available
# if st.session_state["itinerary_data"]:
#     st.markdown("<div class='subheading'>Your Custom Itinerary</div>", unsafe_allow_html=True)
#     with st.expander("View Itinerary Details"):
#         st.markdown(f"<div class='result-container'>{st.session_state['itinerary_data']}</div>", unsafe_allow_html=True)

# # Display the map with itinerary stops if available
# if st.session_state["map_data"]:
#     st.markdown("<div class='subheading'>Itinerary Map</div>", unsafe_allow_html=True)
#     st.write("Explore the stops in your itinerary on the map below:")
#     try:
#         center_coords = st.session_state["map_data"][0]["coordinates"]
#         itinerary_map = folium.Map(location=center_coords, zoom_start=13)

#         for i, stop in enumerate(st.session_state["map_data"]):
#             folium.Marker(
#                 location=stop["coordinates"],
#                 popup=f"{i+1}. {stop['place']} ({stop['start_time']} - {stop['end_time']})",
#                 tooltip=stop["activity"]
#             ).add_to(itinerary_map)
#             if i > 0:
#                 prev_stop = st.session_state["map_data"][i - 1]
#                 folium.PolyLine([prev_stop["coordinates"], stop["coordinates"]], color="blue", weight=2.5).add_to(itinerary_map)

#         # Display the map using st_folium
#         st_folium(itinerary_map, width=700, height=500)
#     except Exception as e:
#         st.error(f"Error displaying map: {e}")
# else:
#     st.warning("Map data is not available. Please check your itinerary.")

# # Display chat history for user interaction tracking
# st.markdown("<div class='subheading'>Chat History</div>", unsafe_allow_html=True)
# st.text_area("Your conversations with Trippy will appear here.", placeholder="Your chat interactions will be displayed here.")























# import streamlit as st
# import requests
# import folium
# from streamlit_folium import st_folium
# from datetime import datetime

# # Set page configuration for Trippy
# st.set_page_config(
#     page_title="Trippy: Your Personalized Tour Guide",
#     page_icon="🧭",
#     layout="centered",
# )

# # Enhanced branding and custom styles
# st.markdown("""
#     <style>
#         /* Background Art */
#         body {
#             background-image: linear-gradient(to right, rgba(240, 248, 255, 0.8), rgba(255, 228, 225, 0.8)),
#                 url('https://source.unsplash.com/1600x900/?tourism,travel,scenery');
#             background-size: cover;
#             background-attachment: fixed;
#         }
        
#         /* Title Style */
#         .title {
#             font-size: 3em;
#             font-weight: bold;
#             color: #E65100;
#             text-align: center;
#             margin-top: 20px;
#         }
        
#         /* Subheading Style */
#         .subheading {
#             font-size: 1.5em;
#             color: #00796B;
#             text-align: center;
#             margin-top: 20px;
#             font-weight: bold;
#         }
        
#         /* Greeting and Instructions */
#         .greeting {
#             font-size: 1.2em;
#             color: #4A148C;
#             text-align: center;
#             margin-top: 10px;
#             font-weight: 500;
#         }
        
#         /* Input Fields Container */
#         .input-container {
#             background-color: rgba(255, 255, 255, 0.9);
#             padding: 20px;
#             border-radius: 10px;
#             box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
#             margin-top: 25px;
#         }
        
#         /* Results and Map Container */
#         .result-container {
#             background-color: #FFFFFF;
#             padding: 20px;
#             border-radius: 10px;
#             margin-top: 15px;
#             box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
#             color: #424242;
#             font-size: 1.1em;
#         }
        
#         /* Map Styling */
#         .map-container {
#             margin-top: 15px;
#             border-radius: 10px;
#             overflow: hidden;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # App Title and Welcome Text
# st.markdown("<div class='title'>Trippy: Your Personalized Tour Guide</div>", unsafe_allow_html=True)
# st.write("Trippy crafts custom one-day travel itineraries based on your preferences. Discover exciting destinations with a tailored journey!")

# # User greeting upon entering their name
# username = st.text_input("Enter your name")
# if username:
#     st.markdown(f"<div class='greeting'>Welcome to Trippy, {username}!</div>", unsafe_allow_html=True)

# # Container for input fields and user preferences
# st.markdown("<div class='subheading'>Tell Us About Your Trip Preferences</div>", unsafe_allow_html=True)
# with st.form("preferences_form"):
#     city = st.text_input("City to Visit", placeholder="e.g., Mumbai, Paris")
#     start_time = st.time_input("Start Time", datetime.strptime("09:00 AM", "%I:%M %p").time())
#     end_time = st.time_input("End Time", datetime.strptime("06:00 PM", "%I:%M %p").time())
#     budget = st.number_input("Budget (INR ₹)", min_value=0, step=500)
#     interests = st.multiselect("Interests", ["Culture", "Adventure", "Food", "Shopping"])
#     starting_point = st.text_input("Starting Point (e.g., hotel location)", placeholder="e.g., Hotel Oberoi")

#     submit_button = st.form_submit_button("Create My Tour")

# # Initialize session state variables to store data
# if "itinerary_data" not in st.session_state:
#     st.session_state["itinerary_data"] = None
# if "map_data" not in st.session_state:
#     st.session_state["map_data"] = None

# # Process preferences on form submission
# if submit_button:
#     if not username or not city or not interests:
#         st.warning("Please fill in all required fields: name, city, and at least one interest.")
#     else:
#         try:
#             # Collect preferences
#             response = requests.post("http://localhost:8000/collect_preferences/", json={
#                 "user_id": username,
#                 "city": city,
#                 "start_time": start_time.strftime("%I:%M %p"),
#                 "end_time": end_time.strftime("%I:%M %p"),
#                 "budget": budget,
#                 "interests": interests,
#                 "starting_point": starting_point
#             })
#             response.raise_for_status()
#             st.success("Preferences saved! Generating your personalized itinerary...")

#             # Generate itinerary
#             itinerary_response = requests.post("http://localhost:8000/generate_itinerary/", json={
#                 "user_id": username,
#                 "city": city,
#                 "start_time": start_time.strftime("%I:%M %p"),
#                 "end_time": end_time.strftime("%I:%M %p"),
#                 "interests": interests,
#                 "budget": budget,
#                 "starting_point": starting_point
#             })
#             itinerary_response.raise_for_status()

#             # Store data in session state
#             data = itinerary_response.json()
#             st.session_state["itinerary_data"] = data.get("itinerary")
#             st.session_state["map_data"] = data.get("map_data")

#         except requests.exceptions.RequestException as e:
#             st.error(f"Error processing your request: {e}")

# # Display itinerary if available
# if st.session_state["itinerary_data"]:
#     st.markdown("<div class='subheading'>Your Trippy Itinerary</div>", unsafe_allow_html=True)
#     with st.expander("View Itinerary Details"):
#         st.markdown(f"<div class='result-container'>{st.session_state['itinerary_data']}</div>", unsafe_allow_html=True)

# # Display map if map data is available
# if st.session_state["map_data"]:
#     st.markdown("<div class='subheading'>Itinerary Map</div>", unsafe_allow_html=True)
#     st.write("Explore the stops on your itinerary with this interactive map:")
#     try:
#         center_coords = st.session_state["map_data"][0]["coordinates"]
#         itinerary_map = folium.Map(location=center_coords, zoom_start=13)

#         for i, stop in enumerate(st.session_state["map_data"]):
#             folium.Marker(
#                 location=stop["coordinates"],
#                 popup=f"{i+1}. {stop['place']} ({stop['start_time']} - {stop['end_time']})",
#                 tooltip=stop["activity"]
#             ).add_to(itinerary_map)
#             if i > 0:
#                 prev_stop = st.session_state["map_data"][i - 1]
#                 folium.PolyLine([prev_stop["coordinates"], stop["coordinates"]], color="blue", weight=2.5).add_to(itinerary_map)

#         # Display the map
#         st_folium(itinerary_map, width=700, height=500)
#     except Exception as e:
#         st.error(f"Error displaying map: {e}")
# else:
#     st.warning("Map data unavailable. Please check if the itinerary was generated correctly.")

# # Display chat history section
# st.markdown("<div class='subheading'>Chat History</div>", unsafe_allow_html=True)
# st.text_area("Your conversations with Trippy will appear here.", placeholder="Interact with the assistant, and messages will display here.")
