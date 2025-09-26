#!/usr/bin/env python3
"""
Test script for the new player functionality
"""

from realgm_stats_api import RealGMStatsAPI
import json

def test_player_functionality():
    """Test the player scraping functionality"""
    api = RealGMStatsAPI()
    
    print("Testing Player Functionality")
    print("=" * 50)
    
    # Test 1: International player profile only
    print("\n1. Testing International player profile...")
    try:
        profile = api.get_player_profile("80999", "Elijah-Stewart")
        print("✅ Profile retrieved successfully")
        print(f"   Name: {profile.get('name')}")
        print(f"   Position: {profile.get('position')}")
        print(f"   Height: {profile.get('height_imperial')} ({profile.get('height_metric')}cm)")
        print(f"   Weight: {profile.get('weight_imperial')} ({profile.get('weight_metric')}kg)")
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
    
    # Test 2: WNBA player profile only
    print("\n2. Testing WNBA player profile...")
    try:
        profile = api.get_player_profile("3000070", "Allisha-Gray")
        print("✅ WNBA Profile retrieved successfully")
        print(f"   Name: {profile.get('name')}")
        print(f"   Position: {profile.get('position')}")
        print(f"   Height: {profile.get('height_imperial')} ({profile.get('height_metric')}cm)")
        print(f"   Weight: {profile.get('weight_imperial')} ({profile.get('weight_metric')}kg)")
    except Exception as e:
        print(f"❌ WNBA Profile test failed: {e}")
    
    # Test 3: International player stats
    print("\n3. Testing International player stats...")
    try:
        stats = api.get_player_stats("80999", "Elijah-Stewart", "International")
        print("✅ International stats retrieved successfully")
        print(f"   Seasons: {len(stats)}")
        if not stats.empty:
            print(f"   Columns: {list(stats.columns)}")
            print(f"   Sample data:")
            print(stats.head(2).to_string())
    except Exception as e:
        print(f"❌ International stats test failed: {e}")
    
    # Test 4: WNBA player stats
    print("\n4. Testing WNBA player stats...")
    try:
        stats = api.get_player_stats("3000070", "Allisha-Gray", "WNBA")
        print("✅ WNBA stats retrieved successfully")
        print(f"   Seasons: {len(stats)}")
        if not stats.empty:
            print(f"   Columns: {list(stats.columns)}")
            print(f"   Sample data:")
            print(stats.head(2).to_string())
    except Exception as e:
        print(f"❌ WNBA stats test failed: {e}")
    
    # Test 5: Complete player data for multiple leagues
    print("\n5. Testing complete player data for multiple leagues...")
    try:
        player_data = api.get_player("80999", "Elijah-Stewart", ["International", "NBA"])
        print("✅ Complete player data retrieved successfully")
        print(f"   Player: {player_data['name']}")
        print(f"   Profile: {player_data['profile']['position']} - {player_data['profile']['height_imperial']}")
        print(f"   Available stats: {list(player_data['stats'].keys())}")
        for league, df in player_data['stats'].items():
            print(f"     {league}: {len(df)} seasons")
    except Exception as e:
        print(f"❌ Complete player data test failed: {e}")
    
    # Test 6: WNBA complete player data
    print("\n6. Testing WNBA complete player data...")
    try:
        player_data = api.get_player("3000070", "Allisha-Gray", ["WNBA"])
        print("✅ WNBA complete player data retrieved successfully")
        print(f"   Player: {player_data['name']}")
        print(f"   Profile: {player_data['profile']['position']} - {player_data['profile']['height_imperial']}")
        print(f"   Available stats: {list(player_data['stats'].keys())}")
        for league, df in player_data['stats'].items():
            print(f"     {league}: {len(df)} seasons")
    except Exception as e:
        print(f"❌ WNBA complete player data test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Player functionality testing complete!")

if __name__ == "__main__":
    test_player_functionality() 