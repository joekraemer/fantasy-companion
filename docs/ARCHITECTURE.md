# 🏗️ System Architecture & Data Flow

> **Status Legend:** ✅ = Implemented & tested | 🚧 = Partially built | 🔲 = Not yet started

```mermaid
flowchart TD
    subgraph Data Sources [Data Layer]
        ESPN["✅ ESPN Fantasy API\n• Live League Rosters\n• Box Scores & Projections\n• Free Agent Universe"]
        NFLV["🔲 NFLverse Parquet Engine\n• WOPR & Target Shares\n• Air Yards & Snaps %\n• EPA & Conversion Rates"]
        ODDS["🔲 Vegas Lines & Weather\n(sourced from NFLverse games.csv)\n• Spreads & O/U Totals\n• Dome / Wind / Temp"]
        SLPR["🔲 Sleeper Trending Engine\n• 24h Waiver Adds/Drops\n• Universal Player ID Map"]
        REDT["🔲 Reddit RSS & NLP\n• r/fantasyfootball Feeds\n• VADER Sentiment Scoring"]
    end

    subgraph Core Engines [Intelligence & Analytics Layer]
        DE["🔲 DataManager & Cache\n• st.cache_data w/ TTL\n• ID Normalization"]
        XFP["🔲 xFP & Opportunity Engine\n• Expected Points Calculation\n• Positive/Negative Regression Flags"]
        STREAM["🔲 Streaming & Lookahead Engine\n• 4-Week D/ST Corridor Model\n• 4-Week Kicker Weather Matrix"]
        SENT["🔲 Sentiment & Buzz Engine\n• Panic / Hype Meter (-1 to +1)\n• Sleeper Add Velocity"]
    end

    subgraph Application [User Interface & Views]
        UI_MATCH["🔲 1. Weekly Matchup Live Center\nHead-to-head simulation & floor/ceiling"]
        UI_STREAM["🔲 2. Multi-Week Streaming Hub\nK & D/ST 4-week lookahead heatmap"]
        UI_WAIVER["🔲 3. Waiver Wire Radar\nxFP + Sleeper Surge + Positive Sentiment"]
        UI_PANIC["🔲 4. Player Panic & Hype Meter\nReddit sentiment breakdown & injury buzz"]
    end

    ESPN --> DE
    NFLV --> DE
    ODDS --> DE
    SLPR --> DE
    REDT --> DE

    DE --> XFP
    DE --> STREAM
    DE --> SENT

    XFP --> UI_MATCH & UI_WAIVER
    STREAM --> UI_STREAM
    SENT --> UI_WAIVER & UI_PANIC
```

---

## Build Order & Dependency Graph

Features must be built in this order. Each tier depends on the one above it.

```mermaid
flowchart LR
    subgraph "Tier 0 — Foundation (no deps)"
        T0A[config.py]
        T0B[nfl_stats.py]
    end

    subgraph "Tier 1 — Core Plumbing"
        T1A[id_mapper.py]
        T1B[data_manager.py]
        T1C[app.py skeleton]
    end

    subgraph "Tier 2 — Independent Engines"
        T2A[sleeper_client.py]
        T2B[sentiment.py]
        T2C[xfp_model.py]
        T2D[streaming.py]
    end

    subgraph "Tier 3 — UI Views"
        T3A[views_matchup.py]
        T3B[views_waivers.py]
        T3C[views_streaming.py]
        T3D[views_sentiment.py]
    end

    T0A --> T1B
    T0B --> T1A
    T0B --> T1B
    T1A --> T2A
    T1B --> T2C & T2D & T1C
    T2A --> T2B
    T2C --> T3A & T3B
    T2D --> T3C
    T2B --> T3B & T3D
```

---

## Data Flow Narrative

1. **Config** (`config.py`) loads `.env` and exposes league credentials + the current NFL season year.
2. **ESPN Client** (`espn_client.py` ✅) fetches live roster, free-agent pool, box scores, and scoring rules from the ESPN API.
3. **NFLverse Loader** (`nfl_stats.py` 🔲) downloads season-level Parquet files (player stats, snap counts) and `games.csv` (schedule, Vegas lines, weather) via HTTPS. This is the backbone of all analytics.
4. **ID Mapper** (`id_mapper.py` 🔲) normalizes player identity across ESPN, Sleeper, and NFLverse using the Sleeper `/players/nfl` universe as the canonical mapping table.
5. **DataManager** (`data_manager.py` 🔲) orchestrates all data sources behind `@st.cache_data`, exposes merged DataFrames to engines (e.g., `get_merged_player_pool()` joins ESPN free agents with NFLverse stats and Vegas lines).
6. **Engines** compute derived analytics: xFP (expected fantasy points from volume + efficiency), Streaming (multi-week D/ST and K projections), Sentiment (Reddit NLP + Sleeper trending velocity).
7. **UI Views** consume engine outputs and render Streamlit pages with Plotly charts, heatmaps, and metric cards.

---

## Modular Directory Layout

```
fantasy-companion/
├── app.py                      # 🔲 Main Streamlit entrypoint
├── requirements.txt            # ✅ Project dependencies
├── .env.example                # ✅ Configuration template
├── .gitignore                  # ✅
├── docs/
│   ├── DATA_ARSENAL.md         # ✅ Public API specifications
│   ├── STREAMING_ENGINE.md     # ✅ Multi-week streaming models
│   └── ARCHITECTURE.md         # ✅ System design & data flow (this file)
├── src/
│   ├── __init__.py             # ✅
│   ├── core/
│   │   ├── __init__.py         # ✅
│   │   ├── config.py           # 🔲 Settings & env parser
│   │   ├── data_manager.py     # 🔲 Master data loader & caching
│   │   └── id_mapper.py        # 🔲 Player ID normalization across platforms
│   ├── engines/
│   │   ├── __init__.py         # ✅
│   │   ├── espn_client.py      # ✅ ESPN League API wrapper
│   │   ├── nfl_stats.py        # 🔲 NFLverse parquet loader
│   │   ├── sleeper_client.py   # 🔲 Sleeper trending + player universe
│   │   ├── streaming.py        # 🔲 Kicker & D/ST multi-week projection engine
│   │   ├── sentiment.py        # 🔲 Reddit search RSS & VADER analyzer
│   │   └── xfp_model.py        # 🔲 Expected Fantasy Points & Regression engine
│   └── ui/
│       ├── __init__.py         # ✅
│       ├── components.py       # 🔲 Custom cards, metrics, and styling
│       ├── views_matchup.py    # 🔲 Matchup Live Center view
│       ├── views_streaming.py  # 🔲 K & D/ST Multi-Week Streaming view
│       ├── views_waivers.py    # 🔲 Waiver Wire Radar view
│       └── views_sentiment.py  # 🔲 Player Panic / Hype Meter view
```
