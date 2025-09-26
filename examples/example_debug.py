from realgm_stats_api.api import RealGMStatsAPI

api = RealGMStatsAPI()
team_name = "Golden State Valkyries"  # Use the slug, not the display name
season = "2025"
stat_type = "Averages"  # or "Totals", "Per_48", etc.

df = api.get_league_stats(
    league_name="wnba",
    season=season,
    stat_type=stat_type,
    team=team_name,
    qualified=True
)

print(df)