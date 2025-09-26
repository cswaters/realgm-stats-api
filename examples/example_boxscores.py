from realgm_stats_api import RealGMStatsAPI, find_league_by_regex
import json
from datetime import datetime

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    print("=== RealGM Boxscore Examples ===\n")
    
    # Example 1: International League (Czech NBL)
    print("1. International League Example (Czech NBL):")
    print("-" * 50)
    
    # Find Czech NBL league
    czech_leagues = find_league_by_regex("Czech.*NBL")
    if not czech_leagues:
        print("Could not find Czech NBL league")
        return
    
    # Get the first matching league (id, name)
    league_id, league_name = czech_leagues[0]
    print(f"Found league: {league_name} (ID: {league_id})")
    
    # Get all dates with games for the league
    dates = api.get_game_dates(league_id, league_name)
    today = datetime.now().strftime("%Y-%m-%d")
    finished_games = [date for date in dates if datetime.strptime(date, "%Y-%m-%d") < datetime.strptime(today, "%Y-%m-%d")]
    
    if finished_games:
        # Get the most recent date with games
        recent_date = finished_games[-1]
        print(f"Getting boxscore links for {recent_date}...")
        boxscore_links = api.get_boxscore_links(league_id, recent_date, league_name)
        
        if boxscore_links:
            print(f"Found {len(boxscore_links)} games:")
            for game_info in boxscore_links:
                print(f"  - {game_info['away_team']} @ {game_info['home_team']} ({game_info['away_score']}-{game_info['home_score']})")
            
            # Get detailed boxscore for the first game
            if boxscore_links:
                print(f"\nGetting detailed boxscore for first game...")
                boxscore = api.get_boxscore(boxscore_links[0])
                print(f"Game ID: {boxscore['game_id']}")
                print(f"Date: {boxscore['date']}")
                print(f"Teams: {boxscore['away_team']} @ {boxscore['home_team']}")
                if 'scores' in boxscore and 'final' in boxscore['scores']:
                    final = boxscore['scores']['final']
                    print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
        else:
            print("No games found for this date")
    else:
        print("No finished games found")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: NBA (Major League)
    print("2. NBA Example (Major League):")
    print("-" * 50)
    
    try:
        # Get NBA game dates
        nba_dates = api.get_game_dates(league_id=163, league_name="nba")
        print(f"Found {len(nba_dates)} NBA game dates")
        
        if nba_dates:
            # Get the most recent date with games
            recent_nba_date = nba_dates[-1]
            print(f"Getting NBA boxscore links for {recent_nba_date}...")
            nba_boxscore_links = api.get_boxscore_links(league_id=163, date=recent_nba_date, league_name="nba")
            
            if nba_boxscore_links:
                print(f"Found {len(nba_boxscore_links)} NBA games:")
                for game_info in nba_boxscore_links:
                    print(f"  - {game_info['away_team']} @ {game_info['home_team']} ({game_info['away_score']}-{game_info['home_score']})")
                
                # Get detailed boxscore for the first game
                if nba_boxscore_links:
                    print(f"\nGetting detailed NBA boxscore for first game...")
                    nba_boxscore = api.get_boxscore(nba_boxscore_links[0])
                    print(f"Game ID: {nba_boxscore['game_id']}")
                    print(f"Date: {nba_boxscore['date']}")
                    print(f"Teams: {nba_boxscore['away_team']} @ {nba_boxscore['home_team']}")
                    if 'scores' in nba_boxscore and 'final' in nba_boxscore['scores']:
                        final = nba_boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
            else:
                print("No NBA games found for this date")
        else:
            print("No NBA game dates found")
    except Exception as e:
        print(f"Error accessing NBA data: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: WNBA (Major League)
    print("3. WNBA Example (Major League):")
    print("-" * 50)
    
    try:
        # Get WNBA game dates
        wnba_dates = api.get_game_dates(league_id=164, league_name="wnba")
        print(f"Found {len(wnba_dates)} WNBA game dates")
        
        if wnba_dates:
            # Get the most recent date with games
            recent_wnba_date = wnba_dates[-1]
            print(f"Getting WNBA boxscore links for {recent_wnba_date}...")
            wnba_boxscore_links = api.get_boxscore_links(league_id=164, date=recent_wnba_date, league_name="wnba")
            
            if wnba_boxscore_links:
                print(f"Found {len(wnba_boxscore_links)} WNBA games:")
                for game_info in wnba_boxscore_links:
                    print(f"  - {game_info['away_team']} @ {game_info['home_team']} ({game_info['away_score']}-{game_info['home_score']})")
                
                # Get detailed boxscore for the first game
                if wnba_boxscore_links:
                    print(f"\nGetting detailed WNBA boxscore for first game...")
                    wnba_boxscore = api.get_boxscore(wnba_boxscore_links[0])
                    print(f"Game ID: {wnba_boxscore['game_id']}")
                    print(f"Date: {wnba_boxscore['date']}")
                    print(f"Teams: {wnba_boxscore['away_team']} @ {wnba_boxscore['home_team']}")
                    if 'scores' in wnba_boxscore and 'final' in wnba_boxscore['scores']:
                        final = wnba_boxscore['scores']['final']
                        print(f"Final Score: {final.get('away', 'N/A')} - {final.get('home', 'N/A')}")
            else:
                print("No WNBA games found for this date")
        else:
            print("No WNBA game dates found")
    except Exception as e:
        print(f"Error accessing WNBA data: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 4: Date Range Example
    print("4. Date Range Example (International League):")
    print("-" * 50)
    
    if finished_games and len(finished_games) >= 2:
        start_date = finished_games[-3]  # 3 days ago
        end_date = finished_games[-1]    # most recent
        
        print(f"Getting boxscores for date range: {start_date} to {end_date}")
        try:
            boxscores_range = api.get_boxscores_for_date_range(
                league_id=league_id, 
                start_date=start_date, 
                end_date=end_date, 
                league_name=league_name
            )
            print(f"Retrieved {len(boxscores_range)} boxscores")
            
            # Show summary of games
            for boxscore in boxscores_range:
                final = boxscore.get('scores', {}).get('final', {})
                print(f"  - {boxscore['away_team']} @ {boxscore['home_team']}: {final.get('away', 'N/A')}-{final.get('home', 'N/A')}")
                
        except Exception as e:
            print(f"Error getting date range boxscores: {e}")
    else:
        print("Not enough game dates available for range example")

if __name__ == "__main__":
    main() 