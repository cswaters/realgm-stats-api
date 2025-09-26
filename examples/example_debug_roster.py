from realgm_stats_api.api import RealGMStatsAPI

api = RealGMStatsAPI()
team_name = "Golden State Valkyries"  # Use the display name
team_id = 7                          # Correct team ID from RealGM
team_slug = "Golden-State-Valkyries" # Correct slug from RealGM
season = "2025"

roster = api.get_team_roster(
    league_name="wnba",
    team_id=team_id,
    team_name=team_slug,
    season=season
)
print(roster)