#!/usr/bin/env python3
"""
Example script demonstrating roster functionality
"""

import json
from realgm_stats_api import RealGMStatsAPI


def main():
    """Demonstrate roster functionality"""
    
    # Initialize API client
    api = RealGMStatsAPI()
    
    # Example: Get roster for ALBA Berlin (German BBL)
    print("=== Single Team Roster Example ===")
    print("Getting roster for ALBA Berlin (German BBL)...")
    
    try:
        roster = api.get_team_roster(
            league_id=15,
            league_name="German-BBL",
            team_id=142,
            team_name="ALBA-Berlin",
            season="2025"
        )
        
        print(f"\nRoster for {roster['team_name']} ({roster['season']} season)")
        print("=" * 60)
        print(f"Total players: {len(roster['roster'])}")
        
        # Display roster table
        if roster['roster']:
            print(f"\n{'#':<4} {'Player':<25} {'Pos':<4} {'Height':<8} {'Weight':<6} {'Age':<4} {'Birth City':<20}")
            print("-" * 90)
            for player in roster['roster']:
                number = str(player.get('number', '-')) if player.get('number') is not None else '-'
                name = str(player.get('name', '-'))[:24]
                position = str(player.get('position', '-'))
                height = str(player.get('height', '-'))
                weight = str(player.get('weight', '-'))
                age = str(player.get('age', '-')) if player.get('age') is not None else '-'
                birth_city = str(player.get('birth_city', '-') or '-')[:19]
                print(f"{number:<4} {name:<25} {position:<4} {height:<8} {weight:<6} {age:<4} {birth_city:<20}")
        
        # Save to JSON file
        with open('alba_berlin_roster.json', 'w') as f:
            json.dump(roster, f, indent=2)
        print(f"\nRoster saved to alba_berlin_roster.json")
        
    except Exception as e:
        print(f"Error getting roster: {e}")
    
    # Example: Get rosters for all teams in German BBL
    print("\n\n=== League Rosters Example ===")
    print("Getting rosters for all teams in German BBL...")
    
    try:
        league_rosters = api.get_league_rosters(
            league_id=15,
            league_name="German-BBL",
            season="2025",
            output_file="german_bbl_rosters.json"
        )
        
        print(f"\nLeague Rosters Summary:")
        print(f"  League: {league_rosters['league_name']}")
        print(f"  Season: {league_rosters['season']}")
        print(f"  Total teams: {league_rosters['total_teams']}")
        print(f"  Successfully scraped: {len([t for t in league_rosters['teams'].values() if 'error' not in t])}")
        print(f"  Errors: {len([t for t in league_rosters['teams'].values() if 'error' in t])}")
        
        print(f"\nTeams with rosters:")
        total_players = 0
        for team_name, roster in league_rosters['teams'].items():
            if 'error' not in roster:
                player_count = len(roster.get('roster', []))
                total_players += player_count
                print(f"  ✅ {team_name} ({player_count} players)")
                
                # Show a sample player from each team
                if roster.get('roster'):
                    sample_player = roster['roster'][0]
                    print(f"    Sample: {sample_player.get('name', 'N/A')} - {sample_player.get('position', 'N/A')}")
            else:
                print(f"  ❌ {team_name} - {roster['error']}")
        
        print(f"\nTotal players across all teams: {total_players}")
        print(f"Full data saved to german_bbl_rosters.json")
        
    except Exception as e:
        print(f"Error getting league rosters: {e}")


if __name__ == "__main__":
    main() 