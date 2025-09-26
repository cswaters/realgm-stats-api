from realgm_stats_api import RealGMStatsAPI
import json
from datetime import datetime

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    print("=== Testing Major League Boxscores with Recent Games (After 2010) ===\n")
    
    # Test NBA
    print("1. NBA Testing:")
    print("-" * 50)
    
    try:
        # Get NBA game dates from the API
        nba_dates = api.get_game_dates(league_id=163, league_name="nba")
        print(f"Found {len(nba_dates)} NBA game dates")
        
        # Filter for dates after 2010
        recent_nba_dates = []
        for date_str in nba_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj.year >= 2010:
                recent_nba_dates.append(date_str)
        
        print(f"Found {len(recent_nba_dates)} NBA dates after 2010")
        
        # Show the first 10 recent dates
        print("First 10 recent NBA dates:")
        for date in recent_nba_dates[:10]:
            print(f"  {date}")
        
        # Test with the first few recent dates that should have games
        test_dates = recent_nba_dates[:5]  # Test first 5 recent dates
        
        for test_date in test_dates:
            print(f"\nTesting NBA boxscores for {test_date}...")
            
            # Get boxscore links for this date
            nba_boxscore_links = api.get_boxscore_links(league_id=163, date=test_date, league_name="nba")
            print(f"Found {len(nba_boxscore_links)} NBA games for {test_date}")
            
            if nba_boxscore_links:
                for i, game_info in enumerate(nba_boxscore_links[:2]):  # Test first 2 games
                    print(f"\nGame {i+1}: {game_info['away_team']} @ {game_info['home_team']}")
                    print(f"Score: {game_info['away_score']}-{game_info['home_score']}")
                    print(f"Game ID: {game_info['game_id']}")
                    
                    # Get detailed boxscore
                    print("Downloading detailed boxscore...")
                    boxscore = api.get_boxscore(game_info)
                    
                    print(f"Boxscore URL: {boxscore['url']}")
                    print(f"Scraped at: {boxscore['scraped_at']}")
                    
                    if 'scores' in boxscore and 'final' in boxscore['scores']:
                        final = boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
                    
                    if 'player_stats' in boxscore:
                        for team_key, team_stats in boxscore['player_stats'].items():
                            print(f"{team_key.upper()} team has {len(team_stats.get('players', []))} players")
                            if team_stats.get('players'):
                                top_scorer = max(team_stats['players'], key=lambda p: p.get('points', 0))
                                print(f"  Top scorer: {top_scorer.get('name', 'N/A')} - {top_scorer.get('points', 0)} pts")
                    
                    print("-" * 40)
                    break  # Only test first game per date
            else:
                print(f"No NBA games found for {test_date}")
            
            if len(nba_boxscore_links) > 0:
                break  # Found games, stop testing more dates
            
    except Exception as e:
        print(f"Error testing NBA: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")
    
    # Test WNBA
    print("2. WNBA Testing:")
    print("-" * 50)
    
    try:
        # Get WNBA game dates from the API
        wnba_dates = api.get_game_dates(league_id=164, league_name="wnba")
        print(f"Found {len(wnba_dates)} WNBA game dates")
        
        # Filter for dates after 2010
        recent_wnba_dates = []
        for date_str in wnba_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj.year >= 2010:
                recent_wnba_dates.append(date_str)
        
        print(f"Found {len(recent_wnba_dates)} WNBA dates after 2010")
        
        # Show the first 10 recent dates
        print("First 10 recent WNBA dates:")
        for date in recent_wnba_dates[:10]:
            print(f"  {date}")
        
        # Test with the first few recent dates that should have games
        test_dates = recent_wnba_dates[:5]  # Test first 5 recent dates
        
        for test_date in test_dates:
            print(f"\nTesting WNBA boxscores for {test_date}...")
            
            # Get boxscore links for this date
            wnba_boxscore_links = api.get_boxscore_links(league_id=164, date=test_date, league_name="wnba")
            print(f"Found {len(wnba_boxscore_links)} WNBA games for {test_date}")
            
            if wnba_boxscore_links:
                for i, game_info in enumerate(wnba_boxscore_links[:2]):  # Test first 2 games
                    print(f"\nGame {i+1}: {game_info['away_team']} @ {game_info['home_team']}")
                    print(f"Score: {game_info['away_score']}-{game_info['home_score']}")
                    print(f"Game ID: {game_info['game_id']}")
                    
                    # Get detailed boxscore
                    print("Downloading detailed boxscore...")
                    boxscore = api.get_boxscore(game_info)
                    
                    print(f"Boxscore URL: {boxscore['url']}")
                    print(f"Scraped at: {boxscore['scraped_at']}")
                    
                    if 'scores' in boxscore and 'final' in boxscore['scores']:
                        final = boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
                    
                    if 'player_stats' in boxscore:
                        for team_key, team_stats in boxscore['player_stats'].items():
                            print(f"{team_key.upper()} team has {len(team_stats.get('players', []))} players")
                            if team_stats.get('players'):
                                top_scorer = max(team_stats['players'], key=lambda p: p.get('points', 0))
                                print(f"  Top scorer: {top_scorer.get('name', 'N/A')} - {top_scorer.get('points', 0)} pts")
                    
                    print("-" * 40)
                    break  # Only test first game per date
            else:
                print(f"No WNBA games found for {test_date}")
            
            if len(wnba_boxscore_links) > 0:
                break  # Found games, stop testing more dates
            
    except Exception as e:
        print(f"Error testing WNBA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 