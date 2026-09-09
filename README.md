# 🏈 Fantasy Companion

An in-season intelligence application for serious fantasy football managers. Built purely on **reliable, open-source data pipelines** and **free public APIs** with zero brittle scraping or paywalled dependencies.

---

## ⚡ Core Features

### 1. ⚔️ Weekly Matchup Live Center
- Real-time sync with your active ESPN league roster and weekly opponent.
- Floor / ceiling simulation based on historical usage rather than single static projection points.
- Real-time game environment context (Vegas implied team totals, weather, wind).

### 2. 🎯 Multi-Week Kicker & D/ST Streaming Engine
- **4-Week Lookahead Heatmap:** Eliminates weekly waiver scrambling by identifying multi-week streaming corridors (e.g. Weeks 3-5 cake matchups).
- **D/ST Metric Modeling:** Combines Vegas opponent implied points, QB pressure/sack vulnerability, turnover rates, and home favorite status.
- **Kicker Metric Modeling:** Evaluates implied team scoring volume, dome/outdoor wind thresholds, and red-zone stall tendencies.

### 3. 📡 Waiver Wire Radar
- Cross-references your league's free agent pool against:
  - **Sleeper 24-Hour Add Velocity:** See who is surging across 100,000+ leagues before your opponents.
  - **Opportunity Surges (WOPR & Snaps):** Detects sudden spikes in target share or red-zone usage.
  - **Expected Fantasy Points (xFP):** Surfaces unrostered players with elite underlying usage.

### 4. 🧠 The Panic & Hype Meter (Reddit Sentiment + NLP)
- Real-time Reddit `r/fantasyfootball` discussion search per player.
- Natural Language Sentiment scoring via `vaderSentiment` (-1.0 Panic to +1.0 Hype).
- Identifies unwarranted community panic (prime buy-low opportunities) and unjustified hype.

---

## 📡 Public Data Arsenal
All data is retrieved from production-grade public datasets:
- **NFLverse Parquet Data:** Target share, air yards, WOPR, EPA, snap counts, player headshots.
- **ESPN League API (`espn-api`):** Live rosters, box scores, scoring settings, and free agent universe.
- **Vegas Odds & Weather Engine:** Point spreads, Over/Unders, implied totals, roof type, wind, and temp.
- **Sleeper Public Trending API:** 24h league-wide add/drop spikes.
- **Reddit RSS Feeds:** Community player discussions analyzed via VADER NLP.

For complete API documentation, see [docs/DATA_ARSENAL.md](docs/DATA_ARSENAL.md).

---

## 🚀 Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joekraemer/fantasy-companion.git
   cd fantasy-companion
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Add your ESPN league credentials
   ```

4. **Launch Application:**
   ```bash
   streamlit run app.py
   ```

---

## 📚 Documentation
- [Data Arsenal & Endpoints](docs/DATA_ARSENAL.md)
- [Multi-Week Streaming Engine](docs/STREAMING_ENGINE.md)
- [System Architecture](docs/ARCHITECTURE.md)
