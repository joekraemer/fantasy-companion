# 🎯 Multi-Week Kicker & D/ST Streaming Engine

Streaming Kickers and Defenses/Special Teams (D/ST) is one of the highest-ROI weekly strategies in fantasy football. Rather than drafting or holding an elite defense through bad matchups, this engine projects **2-week to 4-week streaming corridors** using Vegas lines, defensive pressure rates, opponent offensive vulnerabilities, and weather conditions.

---

## 1. D/ST Multi-Week Model

### A. The Core Scoring Formula
A defense's weekly projection is modeled on five primary predictive factors:

$$\text{DST Score} = w_1 \cdot \text{Baseline} + w_2 \cdot (24 - \text{Opp Implied Pts}) + w_3 \cdot \text{Opp Sack Rate Allowed} + w_4 \cdot \text{Opp Turnover Rate} + w_5 \cdot \text{Home Favorite Bonus}$$

1. **Opponent Implied Total (Vegas):**
   - High correlation to fantasy points allowed. Opponents implied under 18 points receive maximum tier boosts.
2. **Pressure & Sack Vulnerability:**
   - QB pressure rate allowed by the opposing offensive line and QB time-to-throw / sack percentage.
3. **Turnover Tendency:**
   - Opponent turnover-worthy play rate and interception rate per pass attempt.
4. **Game Script / Spread:**
   - Heavy favorites ($\text{Spread} \le -5.5$) force opponents into obvious passing downs, increasing sack and interception volume exponentially.

### B. Multi-Week Corridor Score
Instead of evaluating just the current week, the engine calculates a **Rolling 3-Week Stash Score**:

$$\text{Corridor Score}(w, w+3) = \sum_{k=0}^{2} \gamma^k \cdot \text{DST Score}(w+k) \quad \text{where } \gamma = 0.85$$

This allows you to claim a defense that covers **Weeks 3, 4, and 5** simultaneously, saving precious waiver claims and FAAB.

---

## 2. Kicker (K) Multi-Week Model

### A. The Kicker Success Matrix
Kicker scoring is driven by offensive drive quality and field environment:

1. **High Implied Team Total ($\ge 24.0$):**
   - Correlates with 3+ scoring drives per game.
2. **Favorable Spread (Favorites):**
   - Leading teams settle for field goals in the 2nd half to protect leads, whereas trailing teams are forced to go for it on 4th down.
3. **Dome / Wind Factor:**
   - **Dome / Closed Roof:** $+15\%$ expected FG accuracy and higher coach willingness to attempt 50+ yarders.
   - **High Wind ($\ge 15\text{ mph}$):** $-25\%$ penalty; drives are killed and field goal ranges are shortened.
4. **Red Zone Stall Rate:**
   - Teams with high red-zone trip volume but below-average touchdown conversion rates produce the highest field goal volume.

### B. Lookahead Stash Finder
Flags kickers in your free agent pool that have consecutive dome games or high-scoring matchups over the next 2–4 weeks.

---

## 3. Free Agent Rotation Matrix UI
The application presents a visual **Heatmap Matrix** of all available Kickers and Defenses:
- **Columns:** Current Week, Week + 1, Week + 2, Week + 3.
- **Color Coding:** 
  - 🟢 **Green (Tier 1):** Smash start ($\text{Score} \ge 8.5$)
  - 🟡 **Yellow (Tier 2):** Acceptable floor ($\text{Score} \ge 6.0$)
  - 🔴 **Red (Tier 3):** Avoid / Bench ($\text{Score} < 6.0$)
- **Recommendation Badges:** "Must Add & Hold for 3 Weeks", "One-Week Rental", "Drop After Sunday".
