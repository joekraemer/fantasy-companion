import streamlit as st
from src.core.data_manager import DataManager
from src.core.config import get_settings

st.set_page_config(page_title="Fantasy Companion", page_icon="🏈", layout="wide")

st.title("🏈 Fantasy Companion")

try:
    settings = get_settings()
except EnvironmentError as e:
    st.error(str(e))
    st.stop()

@st.cache_resource
def get_data_manager():
    return DataManager(
        league_id=settings.LEAGUE_ID,
        year=settings.SEASON_YEAR,
        swid=settings.SWID,
        espn_s2=settings.ESPN_S2
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
        # Use team name from settings
        team_name = settings.TEAM_NAME
        client = dm.load_espn_context()
        roster = client.get_team_roster(team_name)
        st.dataframe(roster, use_container_width=True, hide_index=True)
    except ValueError as e:
        st.error(str(e))
