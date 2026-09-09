# 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Data Sources [Data Layer]
        ESPN[ESPN Fantasy API<br/>• Live League Rosters<br/>• Box Scores & Projections<br/>• Free Agent Universe]
        NFLV[NFLverse Parquet Engine<br/>• WOPR & Target Shares<br/>• Air Yards & Snaps %<br/>• EPA & Conversion Rates]
        ODDS[Vegas Lines & Weather<br/>• Spreads & O/U Totals<br/>• Dome / Wind / Temp]
        SLPR[Sleeper Trending Engine<br/>• 24h Waiver Adds/Drops<br/>• Universal Player ID Map]
        REDT[Reddit RSS & NLP<br/>• r/fantasyfootball Feeds<br/>• VADER Sentiment Scoring]
    end

    subgraph Core Engines [Intelligence & Analytics Layer]
        DE[DataManager & Cache<br/>• In-memory LRU / Parquet Cache<br/>• ID Normalization]
        XFP[xFP & Opportunity Engine<br/>• Expected Points Calculation<br/>• Positive/Negative Regression Flags]
        STREAM[Streaming & Lookahead Engine<br/>• 4-Week D/ST Corridor Model<br/>• 4-Week Kicker Weather Matrix]
        SENT[Sentiment & Buzz Engine<br/>• Panic / Hype Meter (-1 to +1)<br/>• Sleeper Add Velocity]
    end

    subgraph Application [User Interface & Views]
        UI_MATCH[1. Weekly Matchup Live Center<br/>Head-to-head simulation & floor/ceiling]
        UI_STREAM[2. Multi-Week Streaming Hub<br/>K & D/ST 4-week lookahead heatmap]
        UI_WAIVER[3. Waiver Wire Radar<br/>xFP + Sleeper Surge + Positive Sentiment]
        UI_PANIC[4. Player Panic & Hype Meter<br/>Reddit sentiment breakdown & injury buzz]
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

## Modular Directory Layout

```
fantasy-companion/
├── app.py                      # Main Streamlit entrypoint
├── requirements.txt            # Project dependencies
├── .env.example                # Configuration template
├── .gitignore
├── docs/
│   ├── DATA_ARSENAL.md         # Public API specifications
│   ├── STREAMING_ENGINE.md     # Multi-week streaming models
│   └── ARCHITECTURE.md         # System design & data flow
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings & env parser
│   │   ├── data_manager.py     # Master data loader & caching
│   │   └── id_mapper.py        # Player ID normalization across platforms
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── espn_client.py      # ESPN League API wrapper
│   │   ├── nfl_stats.py        # NFLverse parquet loader
│   │   ├── streaming.py        # Kicker & D/ST multi-week projection engine
│   │   ├── sentiment.py        # Reddit search RSS & VADER analyzer
│   │   └── xfp_model.py        # Expected Fantasy Points & Regression engine
│   └── ui/
│       ├── __init__.py
│       ├── components.py       # Custom cards, metrics, and styling
│       ├── views_matchup.py    # Matchup Live Center view
│       ├── views_streaming.py  # K & D/ST Multi-Week Streaming view
│       ├── views_waivers.py    # Waiver Wire Radar view
│       └── views_sentiment.py  # Player Panic / Hype Meter view
```
