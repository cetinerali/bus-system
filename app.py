import streamlit as st
import folium
from streamlit_folium import st_folium
from sqlalchemy.orm import Session
import time
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate

from models.base import get_db, engine
from models.landmarks import Landmark
from models.transportation import TransportRoute
from data.landmarks import FAMAGUSTA_CENTER
from utils.map_utils import create_landmark_map, add_landmark_markers, filter_landmarks
from utils.schedule_utils import load_bus_schedules, display_schedule_table
from utils.filter_utils import filter_landmarks_by_distance, filter_landmarks_by_type, filter_landmarks_by_search
from utils.route_utils import create_route_planner, add_route_to_map
from database.init_db import init_database

# Initialize database on startup
init_database()

# 🔵 Mock Bus Movement (Simulating real-time tracking)
BUS_ROUTE = [
    (35.1234, 33.9456), (35.1240, 33.9460), (35.1245, 33.9470),
    (35.1250, 33.9480), (35.1255, 33.9490), (35.1260, 33.9500)
]
if "bus_position_index" not in st.session_state:
    st.session_state.bus_position_index = 0

def update_bus_position():
    """Simulate real-time bus movement."""
    st.session_state.bus_position_index = (st.session_state.bus_position_index + 1) % len(BUS_ROUTE)
    return BUS_ROUTE[st.session_state.bus_position_index]

# 🔵 Authentication Setup
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config["credentials"],
    config["cookie"],
    config["key"],
    config["expiry_days"]
)

# 🔵 Fetch Landmarks with Caching
def get_landmarks(db: Session, search_term: str = "", limit: int = 50) -> list:
    """Fetch landmarks with search filter and limit results."""
    query = db.query(Landmark)
    if search_term:
        search = f"%{search_term.lower()}%"
        query = query.filter(
            (Landmark.name.ilike(search)) | 
            (Landmark.description.ilike(search))
        )
    return [landmark.to_dict() for landmark in query.limit(limit).all()]

# 🔵 Main Streamlit App
def main():
    st.set_page_config(
        page_title="Famagusta Bus System",
        page_icon="🚌",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 🔵 Dark Mode Toggle
    dark_mode = st.sidebar.toggle("Dark Mode", value=False)
    theme = "dark" if dark_mode else "light"
    st.markdown(f"""
        <style>
            body {{ background-color: {'#121212' if dark_mode else '#FFFFFF'}; color: {'#FFFFFF' if dark_mode else '#000000'} }}
        </style>
    """, unsafe_allow_html=True)

    # 🔵 Authentication
    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.write(f"Welcome *{name}*")

        st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Famagusta Bus System</h1>", unsafe_allow_html=True)

        # 🔵 Tabs
        tab3, tab2, tab1, tab4 = st.tabs(["Bus Schedules", "Route Planner", "Landmarks", "Live Bus Tracking"])

        try:
            # Fetch Database Session
            db = next(get_db())

            # Cache landmarks in session state
            if "landmarks" not in st.session_state:
                st.session_state.landmarks = get_landmarks(db)

            landmarks = st.session_state.landmarks

            # 🔵 Live Bus Tracking
            with tab4:
                st.subheader("Live Bus Tracking")
                col1, col2 = st.columns([3, 1])
                with col1:
                    bus_map = create_landmark_map(FAMAGUSTA_CENTER["latitude"], FAMAGUSTA_CENTER["longitude"])
                    bus_lat, bus_lon = update_bus_position()
                    folium.Marker((bus_lat, bus_lon), tooltip="Bus Location", icon=folium.Icon(color='red')).add_to(bus_map)
                    st_folium(bus_map, width=800)
                with col2:
                    st.info(f"Current Bus Location: ({bus_lat}, {bus_lon})")
                    time.sleep(2)  # Simulate movement
                    st.experimental_rerun()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    elif authentication_status is False:
        st.error("Username or password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")

if __name__ == "__main__":
    main()
credentials:
  usernames:
    user1:
      name: "John Doe"
      password: "hashed_password"
    user2:
      name: "Jane Smith"
      password: "hashed_password"
cookie:
  expiry_days: 30
  key: "your_secret_key"
pip install streamlit folium streamlit-folium sqlalchemy pyyaml streamlit-authenticator
