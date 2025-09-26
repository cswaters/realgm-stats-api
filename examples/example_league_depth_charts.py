#!/usr/bin/env python3
"""
Example script demonstrating league depth charts functionality
"""

import json
from realgm_stats_api import RealGMStatsAPI


def main():
    """Demonstrate league depth charts functionality"""
    
    # Initialize API client
    api = RealGMStatsAPI()
    
    # Example: Get teams from German BBL teams page
    print("=== Teams Page Example ===")
    print("Getting teams from German BBL teams page...")
    
    try:
        teams = api.get_teams_from_teams_page(
            league_id=15,
            league_name="German-BBL"
        )
        
        print(f"\nFound {len(teams)} teams in German BBL:")
        for team in teams:
            print(f"  - {team['name']} (ID: {team['id']}, Slug: {team['name_slug']})")
        
        # Save teams list to JSON
        with open('german_bbl_teams.json', 'w') as f:
            json.dump(teams, f, indent=2)
        print(f"\nTeams list saved to german_bbl_teams.json")
        
    except Exception as e:
        print(f"Error getting teams: {e}")
    
    # Example: Get depth charts for all teams in German BBL
    print("\n\n=== League Depth Charts Example ===")
    print("Getting depth charts for all teams in German BBL...")
    
    try:
        league_depth_charts = api.get_league_depth_charts(
            league_id=15,
            league_name="German-BBL",
            season="2025",
            output_file="german_bbl_depth_charts.json"
        )
        
        print(f"\nLeague Depth Charts Summary:")
        print(f"  League: {league_depth_charts['league_name']}")
        print(f"  Season: {league_depth_charts['season']}")
        print(f"  Total teams: {league_depth_charts['total_teams']}")
        print(f"  Successfully scraped: {len([t for t in league_depth_charts['teams'].values() if 'error' not in t])}")
        print(f"  Errors: {len([t for t in league_depth_charts['teams'].values() if 'error' in t])}")
        
        print(f"\nTeams with depth charts:")
        for team_name, depth_chart in league_depth_charts['teams'].items():
            if 'error' not in depth_chart:
                print(f"  ✅ {team_name}")
                # Show a sample depth chart structure
                if 'depth_chart' in depth_chart and 'starters' in depth_chart['depth_chart']:
                    starters = depth_chart['depth_chart']['starters']
                    if 'PG' in starters:
                        pg = starters['PG']
                        stats = pg.get('season_stats', {})
                        points = stats.get('points', 'N/A')
                        print(f"    Starting PG: {pg['name']} ({points} PPG)")
            else:
                print(f"  ❌ {team_name} - {depth_chart['error']}")
        
        print(f"\nFull data saved to german_bbl_depth_charts.json")
        
    except Exception as e:
        print(f"Error getting league depth charts: {e}")


if __name__ == "__main__":
    main() 