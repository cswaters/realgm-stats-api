#!/usr/bin/env python3
"""
Example script demonstrating major league functionality (NBA and WNBA)
"""

import json
from realgm_stats_api import RealGMStatsAPI


def main():
    """Demonstrate major league functionality"""
    
    # Initialize API client
    api = RealGMStatsAPI()
    
    # Example: Get NBA stats
    print("=== NBA Stats Example ===")
    print("Getting NBA stats for 2024-2025 season...")
    
    try:
        nba_stats = api.get_league_stats(
            league_name="nba",
            season="2024-2025",  # Can also use "2025"
            stat_type="Averages",
            qualified=True,
            position="All"
        )
        
        print(f"\nRetrieved {len(nba_stats)} NBA player records")
        print("\nTop 5 NBA scorers:")
        print(nba_stats[['Player', 'Team', 'PPG']].head())
        
        # Save to CSV
        nba_stats.to_csv('nba_stats_2025.csv', index=False)
        print(f"\nNBA stats saved to nba_stats_2025.csv")
        
    except Exception as e:
        print(f"Error getting NBA stats: {e}")
    
    # Example: Get WNBA stats
    print("\n\n=== WNBA Stats Example ===")
    print("Getting WNBA stats for 2025 season...")
    
    try:
        wnba_stats = api.get_league_stats(
            league_name="wnba",
            season="2025",
            stat_type="Averages",
            qualified=True,
            position="All"
        )
        
        print(f"\nRetrieved {len(wnba_stats)} WNBA player records")
        print("\nTop 5 WNBA scorers:")
        print(wnba_stats[['Player', 'Team', 'PPG']].head())
        
        # Save to CSV
        wnba_stats.to_csv('wnba_stats_2025.csv', index=False)
        print(f"\nWNBA stats saved to wnba_stats_2025.csv")
        
    except Exception as e:
        print(f"Error getting WNBA stats: {e}")
    
    # Example: Get NBA teams
    print("\n\n=== NBA Teams Example ===")
    print("Getting NBA teams list...")
    
    try:
        nba_teams = api.get_team_list(
            league_name="nba",
            season="2024-2025"
        )
        
        print(f"\nFound {len(nba_teams)} NBA teams:")
        for team in nba_teams:
            print(f"  - {team['name']} (ID: {team['id']})")
        
        # Save teams list to JSON
        with open('nba_teams.json', 'w') as f:
            json.dump(nba_teams, f, indent=2)
        print(f"\nNBA teams list saved to nba_teams.json")
        
    except Exception as e:
        print(f"Error getting NBA teams: {e}")
    
    # Example: Get WNBA teams
    print("\n\n=== WNBA Teams Example ===")
    print("Getting WNBA teams list...")
    
    try:
        wnba_teams = api.get_team_list(
            league_name="wnba",
            season="2025"
        )
        
        print(f"\nFound {len(wnba_teams)} WNBA teams:")
        for team in wnba_teams:
            print(f"  - {team['name']} (ID: {team['id']})")
        
        # Save teams list to JSON
        with open('wnba_teams.json', 'w') as f:
            json.dump(wnba_teams, f, indent=2)
        print(f"\nWNBA teams list saved to wnba_teams.json")
        
    except Exception as e:
        print(f"Error getting WNBA teams: {e}")
    
    # Example: Get NBA roster (Boston Celtics)
    print("\n\n=== NBA Roster Example ===")
    print("Getting Boston Celtics roster...")
    
    try:
        celtics_roster = api.get_team_roster(
            league_name="nba",
            team_id=2,
            team_name="Boston-Celtics",
            season="2024-2025"
        )
        
        print(f"\nRoster for {celtics_roster['team_name']} ({celtics_roster['season']} season)")
        print("=" * 60)
        print(f"Total players: {len(celtics_roster['roster'])}")
        
        # Display roster table
        if celtics_roster['roster']:
            print(f"\n{'#':<4} {'Player':<25} {'Pos':<4} {'Height':<8} {'Weight':<6} {'Age':<4}")
            print("-" * 60)
            for player in celtics_roster['roster'][:10]:  # Show first 10 players
                number = str(player.get('number', '-')) if player.get('number') is not None else '-'
                name = str(player.get('name', '-'))[:24]
                position = str(player.get('position', '-'))
                height = str(player.get('height', '-'))
                weight = str(player.get('weight', '-'))
                age = str(player.get('age', '-')) if player.get('age') is not None else '-'
                print(f"{number:<4} {name:<25} {position:<4} {height:<8} {weight:<6} {age:<4}")
        
        # Save to JSON file
        with open('celtics_roster.json', 'w') as f:
            json.dump(celtics_roster, f, indent=2)
        print(f"\nCeltics roster saved to celtics_roster.json")
        
    except Exception as e:
        print(f"Error getting Celtics roster: {e}")
    
    # Example: Get WNBA roster (Atlanta Dream)
    print("\n\n=== WNBA Roster Example ===")
    print("Getting Atlanta Dream roster...")
    
    try:
        dream_roster = api.get_team_roster(
            league_name="wnba",
            team_id=1,
            team_name="Atlanta-Dream",
            season="2025"
        )
        
        print(f"\nRoster for {dream_roster['team_name']} ({dream_roster['season']} season)")
        print("=" * 60)
        print(f"Total players: {len(dream_roster['roster'])}")
        
        # Display roster table
        if dream_roster['roster']:
            print(f"\n{'#':<4} {'Player':<25} {'Pos':<4} {'Height':<8} {'Weight':<6} {'Age':<4}")
            print("-" * 60)
            for player in dream_roster['roster'][:10]:  # Show first 10 players
                number = str(player.get('number', '-')) if player.get('number') is not None else '-'
                name = str(player.get('name', '-'))[:24]
                position = str(player.get('position', '-'))
                height = str(player.get('height', '-'))
                weight = str(player.get('weight', '-'))
                age = str(player.get('age', '-')) if player.get('age') is not None else '-'
                print(f"{number:<4} {name:<25} {position:<4} {height:<8} {weight:<6} {age:<4}")
        
        # Save to JSON file
        with open('dream_roster.json', 'w') as f:
            json.dump(dream_roster, f, indent=2)
        print(f"\nDream roster saved to dream_roster.json")
        
    except Exception as e:
        print(f"Error getting Dream roster: {e}")
    
    # Example: Test WNBA depth charts (should fail)
    print("\n\n=== WNBA Depth Charts Test ===")
    print("Testing WNBA depth charts (should not be available)...")
    
    try:
        wnba_depth_chart = api.get_depth_chart(
            league_name="wnba",
            team_id=1,
            team_name="Atlanta-Dream",
            season="2025"
        )
        print("Unexpected: WNBA depth chart worked")
    except Exception as e:
        print(f"Expected error: {e}")
    
    print("\n=== Major League Examples Complete ===")


if __name__ == "__main__":
    main() 