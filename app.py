import os
import streamlit as st
from dotenv import load_dotenv
from src.core.data_manager import DataManager

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Fantasy Companion", page_icon="🏈", layout="wide")

st.title("🏈 Fantasy Companion")

# Verify credentials
league_id = os.getenv("LEAGUE_ID")
swid = os.getenv("SWID")
espn_s2 = os.getenv("espn_s2")

if not all([league_id, swid, espn_s2]):
    st.error("Missing ESPN credentials in `.env`. Please provide LEAGUE_ID, SWID, and espn_s2.")
    st.stop()

@st.cache_resource
def get_data_manager():
    return DataManager(
        league_id=int(league_id),
        year=2024,
        swid=swid,
        espn_s2=espn_s2
    )

dm = get_data_manager()

st.sidebar.header("Settings")
week = st.sidebar.number_input("NFL Week", min_value=1, max_value=18, value=1)

st.header("Free Agent Radar")
with st.spinner("Fetching free agents and merging Vegas odds..."):
    # Fetch top 50 free agents merged with game environment
    df = dm.get_merged_player_pool(week=week, size=50)
    
    if df.empty:
        st.warning("No data found for the requested week.")
    else:
        st.dataframe(
            df[['name', 'position', 'proTeam', 'projectedPoints', 'opponent', 'spread_line', 'total_line', 'roof']],
            use_container_width=True,
            hide_index=True
        )

st.header("My Roster")
with st.spinner("Fetching roster..."):
    try:
        # Assuming the team name is "Turn Your Head and Goff" based on the issue description
        team_name = "Turn Your Head and Goff"
        client = dm.load_espn_context()
        roster = client.get_team_roster(team_name)
        st.dataframe(roster, use_container_width=True, hide_index=True)
    except ValueError as e:
        st.error(str(e))
