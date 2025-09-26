#!/usr/bin/env python3
"""
Comprehensive example script for RealGMStatsAPI: international, NBA, and WNBA
"""
import json
from realgm_stats_api import RealGMStatsAPI

def print_section(title):
    print("\n" + "=" * 10 + f" {title} " + "=" * 10)

def show_stats(df, label):
    print(f"\nTop 5 {label}:")
    print(df[['Player', 'Team', 'PPG']].head())

def show_teams(teams, label):
    print(f"\nFirst 5 {label} teams:")
    for t in teams[:5]:
        print(f"  - {t['name']} (ID: {t['id']})")

def show_roster(roster, label):
    print(f"\nFirst 5 {label} roster entries:")
    for p in roster[:5]:
        number = str(p.get('number', '-') or '-')
        name = str(p.get('name', '-') or '-')[:24]
        position = str(p.get('position', '-') or '-')
        height = str(p.get('height', '-') or '-')
        weight = str(p.get('weight', '-') or '-')
        age = str(p.get('age', '-') or '-')
        print(f"  {number:<3} {name:<25} {position:<4} {height:<8} {weight:<6} {age:<4}")

def slugify(name):
    import re
    slug = re.sub(r'[^\w\s-]', '', name)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.lower()

def main():
    api = RealGMStatsAPI()
    # International league: German BBL
    league_id = 15
    league_name = "German-BBL"
    season = "2025"
    print_section("German BBL Stats")
    stats = api.get_league_stats(league_id=league_id, league_name=league_name, season=season)
    print(f"Total players: {len(stats)}")
    show_stats(stats, "German BBL players")
    print_section("German BBL Teams")
    teams = api.get_team_list(league_id=league_id, league_name=league_name, season=season)
    print(f"Total teams: {len(teams)}")
    show_teams(teams, "German BBL")
    print_section("German BBL Roster")
    team = teams[0]
    team_slug = team.get('name_slug') or slugify(team['name'])
    roster = api.get_team_roster(league_id=league_id, league_name=league_name, team_id=team['id'], team_name=team_slug, season=season)
    print(f"Roster for {roster['team_name']} ({roster['season']}) - {len(roster['roster'])} players")
    show_roster(roster['roster'], roster['team_name'])
    print_section("German BBL Depth Chart")
    depth_chart = api.get_depth_chart(league_id=league_id, league_name=league_name, team_id=team['id'], team_name=team_slug, season=season)
    print(f"Depth chart for {depth_chart['team_name']} ({depth_chart['season']}) roles: {list(depth_chart['depth_chart'].keys())}")
    # NBA
    print_section("NBA Stats")
    nba_stats = api.get_league_stats(league_name="nba", season="2024-2025")
    print(f"Total NBA players: {len(nba_stats)}")
    show_stats(nba_stats, "NBA players")
    print_section("NBA Teams")
    nba_teams = api.get_team_list(league_name="nba", season="2024-2025")
    print(f"Total NBA teams: {len(nba_teams)}")
    show_teams(nba_teams, "NBA")
    print_section("NBA Roster")
    nba_team = next(t for t in nba_teams if t['name'] == "Boston Celtics")
    nba_slug = slugify(nba_team['name'])
    nba_roster = api.get_team_roster(league_name="nba", team_id=nba_team['id'], team_name=nba_slug, season="2024-2025")
    print(f"Roster for {nba_roster['team_name']} ({nba_roster['season']}) - {len(nba_roster['roster'])} players")
    show_roster(nba_roster['roster'], nba_roster['team_name'])
    print_section("NBA Depth Chart")
    nba_depth_chart = api.get_depth_chart(league_name="nba", team_id=nba_team['id'], team_name=nba_slug, season="2024-2025")
    print(f"Depth chart for {nba_depth_chart['team_name']} ({nba_depth_chart['season']}) roles: {list(nba_depth_chart['depth_chart'].keys())}")
    # WNBA
    print_section("WNBA Stats")
    wnba_stats = api.get_league_stats(league_name="wnba", season="2025")
    print(f"Total WNBA players: {len(wnba_stats)}")
    show_stats(wnba_stats, "WNBA players")
    print_section("WNBA Teams")
    wnba_teams = api.get_team_list(league_name="wnba", season="2025")
    print(f"Total WNBA teams: {len(wnba_teams)}")
    show_teams(wnba_teams, "WNBA")
    print_section("WNBA Roster")
    wnba_team = next(t for t in wnba_teams if t['name'] == "Atlanta Dream")
    wnba_slug = slugify(wnba_team['name'])
    wnba_roster = api.get_team_roster(league_name="wnba", team_id=wnba_team['id'], team_name=wnba_slug, season="2025")
    print(f"Roster for {wnba_roster['team_name']} ({wnba_roster['season']}) - {len(wnba_roster['roster'])} players")
    show_roster(wnba_roster['roster'], wnba_roster['team_name'])
    print_section("WNBA Depth Chart (should error)")
    try:
        wnba_depth_chart = api.get_depth_chart(league_name="wnba", team_id=wnba_team['id'], team_name=wnba_slug, season="2025")
        print("Unexpected: WNBA depth chart worked")
    except Exception as e:
        print(f"Expected error: {e}")
    print("\nAll league functionality tested.")

if __name__ == "__main__":
    main() 