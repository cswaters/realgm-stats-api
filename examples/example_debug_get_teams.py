from realgm_stats_api.api import RealGMStatsAPI

api = RealGMStatsAPI()
teams = api.scrape_league_teams("wnba")  # or "nba", or any other league slug

for name, info in teams.items():
    print(f"{name}: ID={info['id']}, Slug={info['slug']}, URL={info['url']}")