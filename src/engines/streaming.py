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
            
            if 'total_line' in home.columns and 'spread_line' in home.columns:
                home['implied_points'] = (home['total_line'] / 2) - (home['spread_line'] / 2)
                home['opp_implied_points'] = (home['total_line'] / 2) + (home['spread_line'] / 2)
            else:
                home['implied_points'] = np.nan
                home['opp_implied_points'] = np.nan
        
        away = df.copy()
        if not away.empty:
            away['team'] = away['away_team']
            away['opponent'] = away['home_team']
            away['is_home'] = False
            
            if 'total_line' in away.columns and 'spread_line' in away.columns:
                away['implied_points'] = (away['total_line'] / 2) + (away['spread_line'] / 2)
                away['opp_implied_points'] = (away['total_line'] / 2) - (away['spread_line'] / 2)
                away['spread_line'] = -away['spread_line']
            else:
                away['implied_points'] = np.nan
                away['opp_implied_points'] = np.nan
        
        combined = pd.concat([home, away]).dropna(subset=['team']).reset_index(drop=True)
        # Use MultiIndex for O(1) row lookups instead of expensive boolean masks
        if not combined.empty:
            combined.set_index(['team', 'week'], inplace=True, drop=False)
        return combined

    def score_dst(self, team: str, week: int) -> float:
        """Scores a D/ST based on Vegas odds."""
        if self.team_games.empty or (team, week) not in self.team_games.index:
            return 0.0 # BYE week
            
        game = self.team_games.loc[(team, week)]
        if isinstance(game, pd.DataFrame):
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
        if self.team_games.empty or (team, week) not in self.team_games.index:
            return 0.0
            
        game = self.team_games.loc[(team, week)]
        if isinstance(game, pd.DataFrame):
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
        gamma = 0.85
        
        for team in teams:
            row = {'Team': team}
            corridor_total = 0.0
            
            for i in range(weeks_ahead):
                week = start_week + i
                if position.upper() == 'DST':
                    score = self.score_dst(team, week)
                else:
                    score = self.score_kicker(team, week)
                    
                row[f'Wk {week}'] = score
                corridor_total += score * (gamma ** i)
                
            row['Corridor'] = round(corridor_total, 2)
            data.append(row)
            
        df = pd.DataFrame(data).sort_values(by='Corridor', ascending=False).reset_index(drop=True)
        return df
