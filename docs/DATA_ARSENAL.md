# 📡 Public Data Arsenal & Integrations

The **Fantasy Companion** relies strictly on battle-tested, high-reliability public APIs, curated data releases, and syndication feeds. No brittle DOM scrapers or paywalled services are required.

---

## 1. NFLverse Data Engine (`nflverse-data`)
- **Protocol:** HTTPS / Parquet (via `pyarrow` & `pandas`)
- **Base Endpoint:** `https://github.com/nflverse/nflverse-data/releases/download/`
- **Authentication:** None (Public)
- **Data Latency:** Updated weekly on Tuesdays / game completion
- **Key Datasets:**
  - `player_stats/player_stats_{year}.parquet`:
    - Volume: Target share, air yards share, WOPR (Weighted Opportunity Rating = $1.5 \times \text{target\_share} + 0.7 \times \text{air\_yards\_share}$).
    - Efficiency & Value: Passing/Rushing/Receiving EPA, PACR, RACR, first downs generated.
    - Media: Official high-resolution NFL player headshot URLs.
  - `pbp/play_by_play_{year}.parquet` _(used by xFP & Streaming engines)_:
    - Play-level EPA, WPA, air yards, yards after catch, rush direction.
    - Sack rate, pressure rate, and interception rate per team (aggregated for D/ST model).
    - Red zone attempts, goal-to-go conversions (feeds Kicker stall rate model).
  - `snap_counts/snap_counts_{year}.parquet`:
    - Snap counts, offensive snap share %, defensive snap share %, special teams snaps.
  - `schedules/games.csv` (`https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv`):
    - Game environment: Stadium name, `roof` (dome, outdoors, closed), `surface` (grass/turf), `temp`, `wind`.
    - Betting lines: `spread_line`, `total_line` (Over/Under), `home_moneyline`, `away_moneyline`, implied team totals.

---

## 2. ESPN Fantasy League API (`espn-api`)
- **Protocol:** HTTPS / JSON REST
- **Base Endpoint:** `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/`
- **Authentication:** `espn_s2` cookie & `SWID` UUID (for private leagues)
- **Key Data Extracted:**
  - Full league roster state: Starters, bench slots, IR designations, lineup locks.
  - Weekly head-to-head box scores (`league.box_scores(week)`).
  - Free agent and waiver wire player pool with ownership % and started %.
  - ESPN stat-by-stat projections (passing, rushing, receiving yards/TDs/turnovers).
  - Official injury status tags (`ACTIVE`, `QUESTIONABLE`, `DOUBTFUL`, `OUT`, `IR`).

---

## 3. Sleeper Public Trending & Player Universe API
- **Protocol:** HTTPS / JSON REST
- **Base Endpoint:** `https://api.sleeper.app/v1/`
- **Authentication:** None (Completely open)
- **Rate Limit:** Generous (1000 req/min)
- **Canonical ID Mapping Role:** The `/players/nfl` endpoint serves as the **master player identity table** for the project. It maps ESPN IDs ↔ Sleeper IDs ↔ Yahoo IDs ↔ Rotowire IDs, enabling cross-platform joins. See `src/core/id_mapper.py`.
- **Key Datasets:**
  - `GET /players/nfl/trending/add?lookback_hours=24&limit=25`:
    - League-wide waiver wire additions across 100,000+ active leagues in real time.
  - `GET /players/nfl/trending/drop?lookback_hours=24&limit=25`:
    - League-wide drops (panic drops, injury replacements).
  - `GET /players/nfl`:
    - Complete NFL player database mapping ESPN IDs, Yahoo IDs, Sleeper IDs, Rotowire IDs, age, draft status, and team depth.

---

## 4. Community Sentiment Engine (Reddit `r/fantasyfootball`)
- **Protocol:** HTTPS / Atom RSS
- **Base Endpoint:** `https://www.reddit.com/r/fantasyfootball/`
- **Authentication:** None (Standard User-Agent header)
- **Key Queries:**
  - Player search feed: `search.rss?q={player_name}&restrict_sr=1&sort=new`
  - Breaking community buzz: `hot.rss?limit=25`
- **NLP Processing:**
  - Processed using `vaderSentiment` (Valence Aware Dictionary and sEntiment Reasoner).
  - Outputs a normalized compound sentiment score between `-1.0` (severe panic / injury negativity) and `+1.0` (high hype / breakout confidence).

---

## 5. Breaking News & Beat Reporter Feeds
- **Protocol:** HTTPS / XML RSS
- **Endpoints:**
  - ESPN NFL Breaking News: `https://www.espn.com/espn/rss/nfl/news`
  - ProFootballTalk / NBC Sports: `https://profootballtalk.nbcsports.com/feed/`
- **Usage:** Provides a filtered real-time feed of coach announcements, practice participation reports (DNP / LP / FP), and depth chart shifts.

---

## Implementation Mapping

| Data Source | Module | Status |
|---|---|---|
| ESPN Fantasy API | `src/engines/espn_client.py` | ✅ Implemented |
| NFLverse Parquets & CSV | `src/engines/nfl_stats.py` | 🔲 Not started |
| Sleeper Trending + ID Map | `src/engines/sleeper_client.py` | 🔲 Not started |
| Reddit RSS + VADER | `src/engines/sentiment.py` | 🔲 Not started |
| News RSS Feeds | `src/engines/sentiment.py` (shared) | 🔲 Not started |
| Cross-platform ID Joins | `src/core/id_mapper.py` | 🔲 Not started |
