#!/usr/bin/env python3
"""
Download WNBA Team Statistics
"""

import requests
from realgm_stats_api.api import RealGMStatsAPI
import pandas as pd
import json
from datetime import datetime

def download_wnba_team_stats(season="2025", stat_type="Averages"):
    """
    Download WNBA team statistics for a given season
    
    Args:
        season: Season year (e.g., "2025")
        stat_type: Type of stats ("Averages", "Totals", "Per_48", etc.)
    """
    # Create API client
    api = RealGMStatsAPI()
    
    print(f"Downloading WNBA team stats for {season} season ({stat_type})...")
    
    # WNBA teams
    wnba_teams = [
        "Atlanta Dream",
        "Chicago Sky", 
        "Connecticut Sun",
        "Dallas Wings",
        "Indiana Fever",
        "Las Vegas Aces",
        "Los Angeles Sparks",
        "Minnesota Lynx",
        "New York Liberty",
        "Phoenix Mercury",
        "Seattle Storm",
        "Washington Mystics",
        "Golden State Valkyries"
    ]
    
    all_team_stats = {}
    
    for team in wnba_teams:
        print(f"Downloading stats for {team}...")
        
        try:
            # Get team stats
            stats_df = api.get_league_stats(
                league_name="wnba",
                season=season,
                stat_type=stat_type,
                team=team,
                qualified=True
            )
            
            # Convert DataFrame to dictionary for JSON serialization
            team_stats = {
                'team': team,
                'season': season,
                'stat_type': stat_type,
                'scraped_at': datetime.now().isoformat(),
                'player_count': len(stats_df),
                'players': stats_df.to_dict('records')
            }
            
            all_team_stats[team] = team_stats
            print(f"  ✓ {len(stats_df)} players found")
            
        except Exception as e:
            print(f"  ✗ Error downloading {team}: {e}")
            all_team_stats[team] = {"error": str(e)}
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wnba_team_stats_{season}_{stat_type}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_team_stats, f, indent=2)
    
    print(f"\nTeam stats saved to {filename}")
    
    # Print summary
    successful_teams = [name for name, data in all_team_stats.items() if "error" not in data]
    failed_teams = [name for name, data in all_team_stats.items() if "error" in data]
    
    print(f"\nSummary:")
    print(f"  Successful: {len(successful_teams)} teams")
    print(f"  Failed: {len(failed_teams)} teams")
    
    if failed_teams:
        print(f"  Failed teams: {', '.join(failed_teams)}")
    
    return all_team_stats

def download_single_team_stats(team_name, season="2025", stat_type="Averages"):
    """
    Download stats for a single WNBA team
    
    Args:
        team_name: Team name (e.g., "Seattle Storm")
        season: Season year
        stat_type: Type of stats
    """
    api = RealGMStatsAPI()
    
    print(f"Downloading stats for {team_name} ({season}, {stat_type})...")
    
    try:
        stats_df = api.get_league_stats(
            league_name="wnba",
            season=season,
            stat_type=stat_type,
            team=team_name,
            qualified=True
        )
        
        print(f"✓ Successfully downloaded stats for {team_name}")
        print(f"  Players: {len(stats_df)}")
        print(f"  Columns: {list(stats_df.columns)}")
        
        # Print top 5 players by points
        if 'PTS' in stats_df.columns:
            top_scorers = stats_df.nlargest(5, 'PTS')[['Player', 'Team', 'PTS']]
            print("\nTop 5 scorers:")
            for _, player in top_scorers.iterrows():
                print(f"  - {player['Player']}: {player['PTS']} points")
        
        return stats_df
        
    except Exception as e:
        print(f"✗ Error downloading stats: {e}")
        return None

def download_league_stats(season="2025", stat_type="Averages"):
    """
    Download all WNBA league stats (not filtered by team)
    
    Args:
        season: Season year
        stat_type: Type of stats
    """
    api = RealGMStatsAPI()
    
    print(f"Downloading WNBA league stats for {season} season ({stat_type})...")
    
    try:
        stats_df = api.get_league_stats(
            league_name="wnba",
            season=season,
            stat_type=stat_type,
            team="All",
            qualified=True
        )
        
        print(f"✓ Successfully downloaded league stats")
        print(f"  Total players: {len(stats_df)}")
        print(f"  Teams represented: {stats_df['Team'].nunique()}")
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wnba_league_stats_{season}_{stat_type}_{timestamp}.csv"
        stats_df.to_csv(filename, index=False)
        
        print(f"League stats saved to {filename}")
        
        return stats_df
        
    except Exception as e:
        print(f"✗ Error downloading league stats: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "league":
            # Download all league stats
            season = sys.argv[2] if len(sys.argv) > 2 else "2025"
            stat_type = sys.argv[3] if len(sys.argv) > 3 else "Averages"
            download_league_stats(season, stat_type)
        elif sys.argv[1] == "teams":
            # Download all team stats
            season = sys.argv[2] if len(sys.argv) > 2 else "2025"
            stat_type = sys.argv[3] if len(sys.argv) > 3 else "Averages"
            download_wnba_team_stats(season, stat_type)
        else:
            # Download single team stats
            team_name = sys.argv[1]
            season = sys.argv[2] if len(sys.argv) > 2 else "2025"
            stat_type = sys.argv[3] if len(sys.argv) > 3 else "Averages"
            download_single_team_stats(team_name, season, stat_type)
    else:
        print("Usage:")
        print("  python download_wnba_team_stats.py league [season] [stat_type]")
        print("  python download_wnba_team_stats.py teams [season] [stat_type]")
        print("  python download_wnba_team_stats.py 'Seattle Storm' [season] [stat_type]")
        print("\nExamples:")
        print("  python download_wnba_team_stats.py league 2025 Averages")
        print("  python download_wnba_team_stats.py teams 2025 Totals")
        print("  python download_wnba_team_stats.py 'Seattle Storm' 2025 Per_48")
        print("\nAvailable stat types:")
        print("  Averages, Totals, Per_48, Per_40, Per_36, Per_Minute, Minute_Per, Misc_Stats, Advanced_Stats") 