#!/usr/bin/env python3
"""
Download WNBA Team Rosters
"""

import requests
from realgm_stats_api.rosters import RosterScraper
import json
from datetime import datetime

def download_wnba_rosters(season="2025"):
    """
    Download all WNBA team rosters for a given season
    
    Args:
        season: Season year (e.g., "2025")
    """
    # Create session and scraper
    session = requests.Session()
    scraper = RosterScraper(session, 'https://basketball.realgm.com')
    
    print(f"Downloading WNBA rosters for {season} season...")
    
    # WNBA teams with their IDs and name slugs
    wnba_teams = [
        {"id": 1, "name": "Atlanta Dream", "name_slug": "Atlanta-Dream"},
        {"id": 2, "name": "Chicago Sky", "name_slug": "Chicago-Sky"},
        {"id": 3, "name": "Connecticut Sun", "name_slug": "Connecticut-Sun"},
        {"id": 4, "name": "Dallas Wings", "name_slug": "Dallas-Wings"},
        {"id": 5, "name": "Indiana Fever", "name_slug": "Indiana-Fever"},
        {"id": 6, "name": "Las Vegas Aces", "name_slug": "Las-Vegas-Aces"},
        {"id": 7, "name": "Los Angeles Sparks", "name_slug": "Los-Angeles-Sparks"},
        {"id": 8, "name": "Minnesota Lynx", "name_slug": "Minnesota-Lynx"},
        {"id": 9, "name": "New York Liberty", "name_slug": "New-York-Liberty"},
        {"id": 10, "name": "Phoenix Mercury", "name_slug": "Phoenix-Mercury"},
        {"id": 11, "name": "Seattle Storm", "name_slug": "Seattle-Storm"},
        {"id": 12, "name": "Washington Mystics", "name_slug": "Washington-Mystics"},
        {"id": 13, "name": "Golden State Valkyries", "name_slug": "Golden-State-Valkyries"}
    ]
    
    all_rosters = {}
    
    for team in wnba_teams:
        print(f"Downloading roster for {team['name']}...")
        
        try:
            roster = scraper.get_team_roster(
                league_name="wnba",
                team_id=team["id"],
                team_name=team["name_slug"],
                season=season
            )
            
            all_rosters[team["name"]] = roster
            print(f"  ✓ {len(roster.get('roster', []))} players found")
            
        except Exception as e:
            print(f"  ✗ Error downloading {team['name']}: {e}")
            all_rosters[team["name"]] = {"error": str(e)}
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wnba_rosters_{season}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_rosters, f, indent=2)
    
    print(f"\nRosters saved to {filename}")
    
    # Print summary
    successful_teams = [name for name, data in all_rosters.items() if "error" not in data]
    failed_teams = [name for name, data in all_rosters.items() if "error" in data]
    
    print(f"\nSummary:")
    print(f"  Successful: {len(successful_teams)} teams")
    print(f"  Failed: {len(failed_teams)} teams")
    
    if failed_teams:
        print(f"  Failed teams: {', '.join(failed_teams)}")
    
    return all_rosters

def download_single_team_roster(team_name, team_id, team_slug, season="2025"):
    """
    Download roster for a single WNBA team
    
    Args:
        team_name: Full team name (e.g., "Seattle Storm")
        team_id: Team ID
        team_slug: Team name slug (e.g., "Seattle-Storm")
        season: Season year
    """
    session = requests.Session()
    scraper = RosterScraper(session, 'https://basketball.realgm.com')
    
    print(f"Downloading roster for {team_name} ({season})...")
    
    try:
        roster = scraper.get_team_roster(
            league_name="wnba",
            team_id=team_id,
            team_name=team_slug,
            season=season
        )
        
        print(f"✓ Successfully downloaded roster for {team_name}")
        print(f"  Players: {len(roster.get('roster', []))}")
        print(f"  Scraped at: {roster.get('scraped_at')}")
        
        # Print player names
        print("\nPlayers:")
        for player in roster.get('roster', []):
            print(f"  - {player.get('name', 'Unknown')} ({player.get('position', 'N/A')})")
        
        return roster
        
    except Exception as e:
        print(f"✗ Error downloading roster: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # Download all teams
            season = sys.argv[2] if len(sys.argv) > 2 else "2025"
            download_wnba_rosters(season)
        else:
            # Download single team
            team_name = sys.argv[1]
            team_id = int(sys.argv[2]) if len(sys.argv) > 2 else 11  # Default to Seattle Storm
            team_slug = sys.argv[3] if len(sys.argv) > 3 else "Seattle-Storm"
            season = sys.argv[4] if len(sys.argv) > 4 else "2025"
            
            download_single_team_roster(team_name, team_id, team_slug, season)
    else:
        print("Usage:")
        print("  python download_wnba_rosters.py all [season]")
        print("  python download_wnba_rosters.py 'Seattle Storm' 11 'Seattle-Storm' [season]")
        print("\nExamples:")
        print("  python download_wnba_rosters.py all 2025")
        print("  python download_wnba_rosters.py 'Seattle Storm' 11 'Seattle-Storm' 2025") 