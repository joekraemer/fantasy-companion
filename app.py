import streamlit as st
import pandas as pd
from src.core.data_manager import DataManager
from src.core.config import get_settings

st.set_page_config(page_title="Fantasy Companion", page_icon="🏈", layout="wide")

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
        team_name=settings.TEAM_NAME,
        swid=settings.SWID,
        espn_s2=settings.ESPN_S2
    )

dm = get_data_manager()

# --- Sidebar Config ---
st.sidebar.header("Settings")

try:
    client = dm.load_espn_context()
    league_name = getattr(client.league, 'settings', None)
    league_name_str = getattr(league_name, 'name', f"League {settings.LEAGUE_ID}")
    st.sidebar.subheader(league_name_str)
except Exception:
    st.sidebar.subheader(f"League {settings.LEAGUE_ID}")

selected_week = st.sidebar.number_input("NFL Week", min_value=1, max_value=18, value=1)

nav_option = st.sidebar.radio(
    "Navigation", 
    ["Home", "Matchup Center", "Streaming Hub", "Waiver Radar", "Panic Meter"]
)

# --- Page Routing ---
if nav_option == "Home":
    st.title("🏈 Fantasy Companion")
    st.markdown("Welcome to the **Fantasy Companion**. All data sources loaded successfully.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("My Roster")
        try:
            roster = dm.get_my_roster(settings.TEAM_NAME)
            if roster is not None and not roster.empty:
                st.dataframe(roster, use_container_width=True, hide_index=True)
            else:
                st.info("No players found on your roster.")
        except Exception as e:
            st.error(f"Error loading roster: {e}")
            
    with col2:
        st.header("Free Agent Pool")
        try:
            fa_list = dm.get_free_agent_pool(size=100)
            st.metric("Free Agents Loaded", len(fa_list))
            if fa_list is not None and not fa_list.empty:
                st.dataframe(pd.DataFrame(fa_list), use_container_width=True, hide_index=True)
            else:
                st.info("No free agents found.")
        except Exception as e:
            st.error(f"Error loading free agents: {e}")
            
    st.header(f"NFL Schedule (Week {selected_week})")
    try:
        week_schedule = dm.get_weekly_schedule(selected_week)
        if not week_schedule.empty:
            st.dataframe(week_schedule, use_container_width=True, hide_index=True)
        else:
            st.info("No games found for this week.")
    except Exception as e:
        st.error(f"Error loading schedule: {e}")

elif nav_option == "Matchup Center":
    try:
        from src.ui.views_matchup import render_matchup
        render_matchup(dm, selected_week, settings)
    except ImportError:
        st.info("Matchup Center — Coming Soon")
        
elif nav_option == "Streaming Hub":
    try:
        from src.ui.views_streaming import render_streaming
        render_streaming(dm, selected_week, settings)
    except ImportError:
        st.info("Streaming Hub — Coming Soon")
        
elif nav_option == "Waiver Radar":
    try:
        from src.ui.views_waiver import render_waiver
        render_waiver(dm, selected_week, settings)
    except ImportError:
        st.info("Waiver Radar — Coming Soon")
        
elif nav_option == "Panic Meter":
    try:
        from src.ui.views_panic import render_panic
        render_panic(dm, selected_week, settings)
    except ImportError:
        st.info("Panic Meter — Coming Soon")
