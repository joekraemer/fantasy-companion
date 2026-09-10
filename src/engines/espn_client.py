import os
from typing import List, Dict, Any, Optional
from espn_api.football import League

class ESPNClient:
    """
    Wrapper for the espn-api library to manage the fantasy football league context.
    """
    def __init__(self, league_id: int, year: int, swid: Optional[str] = None, espn_s2: Optional[str] = None):
        """
        Initializes the ESPN League client. 
        For private leagues, both swid and espn_s2 are required.
        """
        self.league_id = league_id
        self.year = year
        self.swid = swid
        self.espn_s2 = espn_s2
        
        self.league = League(
            league_id=self.league_id,
            year=self.year,
            espn_s2=self.espn_s2,
            swid=self.swid
        )

    def get_team_by_name(self, team_name: str):
        """Finds and returns a Team object by its name."""
        for team in self.league.teams:
            if team.team_name.lower() == team_name.lower():
                return team
        return None

    def get_team_roster(self, team_name: str) -> List[Dict[str, Any]]:
        """
        Returns a parsed list of players for a specific team.
        """
        team = self.get_team_by_name(team_name)
        if not team:
            raise ValueError(f"Team '{team_name}' not found in the league.")
            
        roster = []
        for player in team.roster:
            roster.append({
                "name": player.name,
                "position": getattr(player, 'position', 'UNKNOWN'),
                "injuryStatus": getattr(player, 'injuryStatus', 'ACTIVE'),
                "proTeam": getattr(player, 'proTeam', 'FA'),
                "eligibleSlots": getattr(player, 'eligibleSlots', [])
            })
        return roster

    def get_free_agents(self, size: int = 100) -> List[Dict[str, Any]]:
        """
        Returns a list of the top available free agents.
        """
        fa_pool = []
        free_agents = self.league.free_agents(size=size)
        
        for player in free_agents:
            fa_pool.append({
                "name": player.name,
                "position": getattr(player, 'position', 'UNKNOWN'),
                "injuryStatus": getattr(player, 'injuryStatus', 'ACTIVE'),
                "proTeam": getattr(player, 'proTeam', 'FA'),
                "projectedPoints": getattr(player, 'projected_points', 0)
            })
        return fa_pool

    def get_scoring_rules(self) -> Dict[str, Any]:
        """
        Returns a simplified view of the league scoring settings.
        """
        if hasattr(self.league, 'settings') and hasattr(self.league.settings, 'scoring_format'):
            return self.league.settings.scoring_format
        return {}
