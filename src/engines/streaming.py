import pandas as pd
import numpy as np

class StreamingEngine:
    """
    Analytics engine for multi-week D/ST and Kicker streaming projections.
    Uses a simplified tier-based Vegas scoring model.
    """
    def __init__(self, schedule_df: pd.DataFrame):
        self.schedule_df = schedule_df
        self.team_games = self._melt_schedule(schedule_df)
        
    def _melt_schedule(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
            
        home = df.copy()
        if not home.empty:
            home['team'] = home['home_team']
            home['opponent'] = home['away_team']
            home['is_home'] = True
            # Home Implied = (Total / 2) - (Spread / 2)
            # Away Implied = (Total / 2) + (Spread / 2)
            home['implied_points'] = (home['total_line'] / 2) - (home['spread_line'] / 2)
            home['opp_implied_points'] = (home['total_line'] / 2) + (home['spread_line'] / 2)
        
        away = df.copy()
        if not away.empty:
            away['team'] = away['away_team']
            away['opponent'] = away['home_team']
            away['is_home'] = False
            away['implied_points'] = (away['total_line'] / 2) + (away['spread_line'] / 2)
            away['opp_implied_points'] = (away['total_line'] / 2) - (away['spread_line'] / 2)
            # Flip spread from the away team's perspective
            away['spread_line'] = -away['spread_line']
        
        combined = pd.concat([home, away]).dropna(subset=['team']).reset_index(drop=True)
        return combined

    def score_dst(self, team: str, week: int) -> float:
        """Scores a D/ST based on Vegas odds."""
        if self.team_games.empty:
            return 0.0
            
        game = self.team_games[(self.team_games['team'] == team) & (self.team_games['week'] == week)]
        if game.empty:
            return 0.0 # BYE week
            
        game = game.iloc[0]
        score = 0.0
        
        opp_implied = game.get('opp_implied_points', np.nan)
        spread = game.get('spread_line', np.nan)
        roof = game.get('roof', '')
        
        if pd.notna(opp_implied):
            if opp_implied <= 17:
                score += 5.0 # +3 (for <=20) and +2 (for <=17)
            elif opp_implied <= 20:
                score += 3.0
                
        if pd.notna(spread) and game.get('is_home', False):
            if spread <= -6:
                score += 3.0 # +1 (for <=-3) and +2 (for <=-6)
            elif spread <= -3:
                score += 1.0
                
        if pd.notna(roof) and str(roof).lower() in ['dome', 'closed']:
            score += 1.0
            
        return float(score)

    def score_kicker(self, team: str, week: int) -> float:
        """Scores a Kicker based on Vegas odds and weather."""
        if self.team_games.empty:
            return 0.0
            
        game = self.team_games[(self.team_games['team'] == team) & (self.team_games['week'] == week)]
        if game.empty:
            return 0.0
            
        game = game.iloc[0]
        score = 0.0
        
        implied = game.get('implied_points', np.nan)
        roof = game.get('roof', '')
        wind = game.get('wind', np.nan)
        
        if pd.notna(implied):
            if implied >= 27:
                score += 5.0 # +3 (for >=24) and +2 (for >=27)
            elif implied >= 24:
                score += 3.0
                
        if pd.notna(roof) and str(roof).lower() in ['dome', 'closed']:
            score += 1.5
            
        if pd.notna(wind) and wind >= 15.0:
            score -= 2.0
            
        return float(score)
        
    def corridor_score(self, team: str, start_week: int, weeks_ahead: int = 3, position: str = 'DST') -> float:
        """Rolling discounted sum (decay gamma=0.85)."""
        total = 0.0
        gamma = 0.85
        
        for i in range(weeks_ahead):
            week = start_week + i
            if position.upper() == 'DST':
                score = self.score_dst(team, week)
            else:
                score = self.score_kicker(team, week)
                
            total += score * (gamma ** i)
            
        return round(total, 2)
        
    def get_streaming_matrix(self, position: str, start_week: int, weeks_ahead: int = 3) -> pd.DataFrame:
        """Returns a Heatmap-ready DataFrame for all teams."""
        if self.team_games.empty:
            return pd.DataFrame()
            
        teams = self.team_games['team'].dropna().unique()
        data = []
        
        for team in teams:
            row = {'Team': team}
            for i in range(weeks_ahead):
                week = start_week + i
                if position.upper() == 'DST':
                    row[f'Wk {week}'] = self.score_dst(team, week)
                else:
                    row[f'Wk {week}'] = self.score_kicker(team, week)
            row['Corridor'] = self.corridor_score(team, start_week, weeks_ahead, position)
            data.append(row)
            
        df = pd.DataFrame(data).sort_values(by='Corridor', ascending=False).reset_index(drop=True)
        return df
