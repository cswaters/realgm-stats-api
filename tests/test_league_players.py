#!/usr/bin/env python3
"""
Test script for the new league players functionality
"""

from realgm_stats_api import RealGMStatsAPI

def test_league_players():
    """Test the league players scraping functionality"""
    api = RealGMStatsAPI()
    
    print("Testing League Players Functionality")
    print("=" * 50)
    
    # Test 1: WNBA players
    print("\n1. Testing WNBA players...")
    try:
        wnba_players = api.get_league_players("WNBA", "2025")
        print("✅ WNBA players retrieved successfully")
        print(f"   Total players: {len(wnba_players)}")
        print(f"   Columns: {list(wnba_players.columns)}")
        if not wnba_players.empty:
            print("   Sample data:")
            print(wnba_players.head(3).to_string())
    except Exception as e:
        print(f"❌ WNBA players test failed: {e}")
    
    # Test 2: NBA players
    print("\n2. Testing NBA players...")
    try:
        nba_players = api.get_league_players("NBA", "2025")
        print("✅ NBA players retrieved successfully")
        print(f"   Total players: {len(nba_players)}")
        print(f"   Columns: {list(nba_players.columns)}")
        if not nba_players.empty:
            print("   Sample data:")
            print(nba_players.head(3).to_string())
    except Exception as e:
        print(f"❌ NBA players test failed: {e}")
    
    # Test 3: WNBA players with team filter
    print("\n3. Testing WNBA players with team filter...")
    try:
        wnba_team_players = api.get_league_players("WNBA", "2025", "Chicago-Sky")
        print("✅ WNBA team players retrieved successfully")
        print(f"   Total players: {len(wnba_team_players)}")
        if not wnba_team_players.empty:
            print("   Sample data:")
            print(wnba_team_players.head(3).to_string())
    except Exception as e:
        print(f"❌ WNBA team players test failed: {e}")
    
    # Test 4: NBA players with team filter
    print("\n4. Testing NBA players with team filter...")
    try:
        nba_team_players = api.get_league_players("NBA", "2025", "Atlanta Hawks")
        print("✅ NBA team players retrieved successfully")
        print(f"   Total players: {len(nba_team_players)}")
        if not nba_team_players.empty:
            print("   Sample data:")
            print(nba_team_players.head(3).to_string())
    except Exception as e:
        print(f"❌ NBA team players test failed: {e}")
    
    print("\n" + "=" * 50)
    print("League players functionality testing complete!")

if __name__ == "__main__":
    test_league_players() 