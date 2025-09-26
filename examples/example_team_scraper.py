#!/usr/bin/env python3
"""
Example script showing how to use the new team scraping utility functions
"""

from realgm_stats_api.api import RealGMStatsAPI

def main():
    api = RealGMStatsAPI()
    
    # Example 1: Print all WNBA teams
    print("=== WNBA Teams ===")
    api.print_league_teams("wnba")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Get team mapping for WNBA
    print("=== WNBA Team Mapping ===")
    wnba_teams = api.scrape_league_teams("wnba")
    for team_name, info in wnba_teams.items():
        print(f"{team_name}: ID={info['id']}, Slug={info['slug']}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Generate Python code for team mapping
    print("=== Generated Python Code ===")
    code = api.get_team_mapping_for_code("wnba")
    print(code)
    
    print("\n" + "="*60 + "\n")
    
    # Example 4: Try with NBA
    print("=== NBA Teams ===")
    try:
        api.print_league_teams("nba")
    except Exception as e:
        print(f"Error with NBA: {e}")

if __name__ == "__main__":
    main() 