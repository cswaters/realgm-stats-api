from realgm_stats_api import RealGMStatsAPI
from datetime import datetime, timedelta
import json

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    print("=== RealGM Upcoming Games Example (WNBA) ===\n")
    
    try:
        # Get WNBA game dates
        wnba_dates = api.get_game_dates(league_id=164, league_name="wnba")
        print(f"Found {len(wnba_dates)} WNBA game dates")
        
        if wnba_dates:
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find upcoming dates (today and future)
            upcoming_dates = [date for date in wnba_dates if date >= today]
            
            if upcoming_dates:
                print(f"Found {len(upcoming_dates)} upcoming dates with games")
                
                # Get upcoming games for the next few dates
                for i, date in enumerate(upcoming_dates[:5]):  # Show next 5 dates
                    print(f"\n--- Games for {date} ---")
                    
                    upcoming_games = api.get_upcoming_games(league_id=164, date=date, league_name="wnba")
                    
                    if upcoming_games:
                        print(f"Found {len(upcoming_games)} upcoming games:")
                        for game in upcoming_games:
                            print(f"  {game['time']} | {game['away']} @ {game['home']} | {game['location']} | {game['type']}")
                    else:
                        print("No upcoming games found for this date")
            else:
                print("No upcoming game dates found")
                
                # If no upcoming dates, show the most recent date with games
                if wnba_dates:
                    most_recent = wnba_dates[-1]
                    print(f"\nMost recent date with games: {most_recent}")
                    upcoming_games = api.get_upcoming_games(league_id=164, date=most_recent, league_name="wnba")
                    
                    if upcoming_games:
                        print(f"Found {len(upcoming_games)} games:")
                        for game in upcoming_games:
                            print(f"  {game['time']} | {game['away']} @ {game['home']} | {game['location']} | {game['type']}")
        else:
            print("No WNBA game dates found")
            
    except Exception as e:
        print(f"Error accessing WNBA upcoming games: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 