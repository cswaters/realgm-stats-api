from realgm_stats_api import RealGMStatsAPI
import json

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    print("=== WNBA Boxscore Output Format ===\n")
    
    # Test with a specific WNBA game from 2015
    test_date = "2015-06-05"
    
    try:
        print(f"Getting WNBA boxscore links for {test_date}...")
        wnba_boxscore_links = api.get_boxscore_links(league_id=164, date=test_date, league_name="wnba")
        print(f"Found {len(wnba_boxscore_links)} WNBA games for {test_date}")
        
        if wnba_boxscore_links:
            # Test the first game
            game_info = wnba_boxscore_links[0]
            print(f"\nTesting game: {game_info['away_team']} @ {game_info['home_team']}")
            print(f"Game ID: {game_info['game_id']}")
            print(f"URL: {game_info['url']}")
            
            # Get the detailed boxscore
            print("\nDownloading detailed boxscore...")
            boxscore = api.get_boxscore(game_info)
            
            print("\n" + "="*60)
            print("DETAILED BOXSCORE OUTPUT FORMAT")
            print("="*60)
            
            # Show the complete structure
            print("\n1. BASIC GAME INFO:")
            print(f"   game_id: {boxscore['game_id']}")
            print(f"   date: {boxscore['date']}")
            print(f"   url: {boxscore['url']}")
            print(f"   away_team: {boxscore['away_team']}")
            print(f"   home_team: {boxscore['home_team']}")
            print(f"   scraped_at: {boxscore['scraped_at']}")
            
            print("\n2. SCORES:")
            if 'scores' in boxscore:
                scores = boxscore['scores']
                print(f"   away_abbr: {scores.get('away_abbr', 'N/A')}")
                print(f"   home_abbr: {scores.get('home_abbr', 'N/A')}")
                print(f"   away_record: {scores.get('away_record', 'N/A')}")
                print(f"   home_record: {scores.get('home_record', 'N/A')}")
                print(f"   final: {scores.get('final', {})}")
                print(f"   quarters: {scores.get('quarters', {})}")
            
            print("\n3. ADVANCED STATS:")
            if 'advanced_stats' in boxscore:
                advanced = boxscore['advanced_stats']
                for key, value in advanced.items():
                    print(f"   {key}: {value}")
            
            print("\n4. FOUR FACTORS:")
            if 'four_factors' in boxscore:
                four_factors = boxscore['four_factors']
                for key, value in four_factors.items():
                    print(f"   {key}: {value}")
            
            print("\n5. PLAYER STATS:")
            if 'player_stats' in boxscore:
                player_stats = boxscore['player_stats']
                for team_key, team_data in player_stats.items():
                    print(f"\n   {team_key.upper()} TEAM:")
                    print(f"     Number of players: {len(team_data.get('players', []))}")
                    
                    # Show first player as example
                    if team_data.get('players'):
                        first_player = team_data['players'][0]
                        print(f"     First player example:")
                        for key, value in first_player.items():
                            print(f"       {key}: {value}")
                    
                    # Show team totals
                    if 'totals' in team_data:
                        totals = team_data['totals']
                        print(f"     Team totals:")
                        for key, value in totals.items():
                            print(f"       {key}: {value}")
            
            print("\n6. DEPTH CHARTS:")
            if 'depth_charts' in boxscore:
                depth_charts = boxscore['depth_charts']
                for team_key, team_depth in depth_charts.items():
                    print(f"\n   {team_key.upper()} TEAM:")
                    for role, positions in team_depth.items():
                        print(f"     {role}:")
                        for pos, player_info in positions.items():
                            print(f"       {pos}: {player_info}")
            
            print("\n7. METADATA:")
            if 'metadata' in boxscore:
                metadata = boxscore['metadata']
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            
            print("\n" + "="*60)
            print("COMPLETE JSON STRUCTURE:")
            print("="*60)
            print(json.dumps(boxscore, indent=2, default=str))
            
        else:
            print("No WNBA games found for this date")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 