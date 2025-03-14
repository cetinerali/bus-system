import streamlit as st
import folium
from streamlit_folium import st_folium
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate
import time
import random
import pandas as pd
import networkx as nx

from models.base import get_db
from models.landmarks import Landmark
from models.transportation import TransportRoute
from utils.map_utils import create_map, add_landmark_markers
from database.init_db import init_database

# Initialize database
init_database()

# Load authentication data
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config["credentials"],
    config["cookie"],
    config["key"],
    config["expiry_days"]
)

# Streamlit UI Setup
st.set_page_config(
    page_title="Famagusta Bus System",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome *{name}*!")

    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Famagusta Bus System</h1>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Interactive Map", "AI Route Planner", "Live Bus Tracking", "User Rewards", "Leaderboard", "Statistics & Complaints"
    ])

    with tab1:
        st.subheader("Interactive Map with Landmarks")
        map_famagusta = create_map(35.1264, 33.9391)
        add_landmark_markers(map_famagusta, [
            {"name": "Salamis Ruins", "lat": 35.1872, "lon": 33.8914, "desc": "Ancient ruins of Salamis."},
            {"name": "Othello Castle", "lat": 35.1258, "lon": 33.9393, "desc": "Historic fortress from Shakespeare's Othello."},
            {"name": "Lala Mustafa Pasha Mosque", "lat": 35.1266, "lon": 33.9383, "desc": "A Gothic church converted into a mosque."}
        ])
        st_folium(map_famagusta, width=800)

    with tab2:
        st.subheader("AI-Powered Route Planner")

        # Create Graph for Shortest Path Calculation
        G = nx.Graph()
        G.add_edge("Salamis Ruins", "Othello Castle", weight=random.uniform(1.0, 5.0))
        G.add_edge("Othello Castle", "Lala Mustafa Pasha Mosque", weight=random.uniform(1.0, 5.0))
        G.add_edge("Lala Mustafa Pasha Mosque", "Salamis Ruins", weight=random.uniform(1.0, 5.0))

        start = st.selectbox("Select Start Point", list(G.nodes))
        end = st.selectbox("Select Destination", list(G.nodes))

        if start != end:
            shortest_path = nx.shortest_path(G, source=start, target=end, weight="weight")
            estimated_time = sum(G[u][v]["weight"] for u, v in zip(shortest_path[:-1], shortest_path[1:]))
            st.success(f"🚍 AI-Optimized Route: {' → '.join(shortest_path)}\n\n⏳ Estimated Travel Time: {estimated_time:.2f} mins.")

    with tab3:
        st.subheader("Live Bus Tracking")
        bus_map = create_map(35.1264, 33.9391)
        folium.Marker((35.1250, 33.9480), tooltip="Bus Location", icon=folium.Icon(color='red')).add_to(bus_map)
        st_folium(bus_map, width=800)

    with tab4:
        st.subheader("User Rewards & Badges")
        trips_taken = st.number_input("How many bus trips have you taken this week?", min_value=0, step=1)

        if trips_taken:
            energy_saved = trips_taken * 0.8
            time_saved = trips_taken * 5
            st.success(f"🏆 You saved **{energy_saved} kWh** of energy and **{time_saved} minutes** by taking the bus!")

            # Reward System
            if trips_taken >= 10:
                st.balloons()
                st.success("🥇 Congratulations! You've earned the **Frequent Traveler Badge**! 🎉")
            elif trips_taken >= 5:
                st.success("🥈 Great job! You've earned the **Eco-Friendly Commuter Badge**! 🚍")

    with tab5:
        st.subheader("🏆 Leaderboard")
        leaderboard_data = pd.DataFrame({
            "User": ["John", "Jane", "Alex", "Emma", "Michael"],
            "Trips Taken": [15, 12, 10, 9, 7]
        }).sort_values(by="Trips Taken", ascending=False)
        st.table(leaderboard_data)

    with tab6:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Transport Usage Statistics")
            data = pd.DataFrame({
                "Date": pd.date_range(start="2023-01-01", periods=7, freq="D"),
                "Daily Users": [random.randint(50, 200) for _ in range(7)]
            })
            st.line_chart(data.set_index("Date"))

        with col2:
            st.subheader("📝 Submit a Complaint")
            user_feedback = st.text_area("Describe your issue or feedback:")
            if st.button("Submit Complaint"):
                st.success("✅ Your complaint has been recorded. Thank you for your feedback!")

elif authentication_status is False:
    st.error("Incorrect username or password.")
elif authentication_status is None:
    st.warning("Please enter your username and password.")
