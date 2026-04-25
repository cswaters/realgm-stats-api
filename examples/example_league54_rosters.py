#!/usr/bin/env python3
"""
Example: Pull rosters for League 54 (Italian Serie A2 Basket)

This example demonstrates how to use the new resolver system to pull
team rosters from the Italian Serie A2 Basketball league using either
league ID or league name.
"""

from realgm_stats_api import RealGMStatsAPI
import json
from datetime import datetime


def main():
    # Initialize the API client
    api = RealGMStatsAPI()

    print("🏀 Italian Serie A2 Basket Roster Example")
    print("=" * 50)

    # Method 1: Using League ID (recommended for reliability)
    print("\n📋 Method 1: Using League ID")
    print("-" * 30)

    try:
        print("Getting rosters using League ID 54...")

        # The new resolver system allows us to use just the league ID or name
        rosters_by_id = api.get_league_rosters(
            league=54,  # Much cleaner than the old league_id + league_name
            season="2025"
        )

        print(f"✅ Successfully retrieved rosters for {len(rosters_by_id)} teams")

        # Display some roster information
        for team_name, roster_data in list(rosters_by_id.items())[:3]:  # Show first 3 teams
            print(f"\n🏀 {team_name}")
            if 'roster' in roster_data and roster_data['roster']:
                players = roster_data['roster']
                print(f"   📊 Players: {len(players)}")

                # Show first few players
                for i, player in enumerate(players[:3]):
                    name = player.get('name', 'Unknown')
                    position = player.get('position', 'N/A')
                    height = player.get('height', 'N/A')
                    print(f"   {i+1}. {name} ({position}) - {height}")

                if len(players) > 3:
                    print(f"   ... and {len(players) - 3} more players")
            else:
                print("   ❌ No roster data available")

    except Exception as e:
        print(f"❌ Error with League ID method: {e}")

    # Method 2: Using League Name (also works with the new resolver)
    print("\n\n📋 Method 2: Using League Name")
    print("-" * 35)

    try:
        print("Getting rosters using league name...")

        # The resolver can handle the full league name
        rosters_by_name = api.get_league_rosters(
            league="Italian Serie A2 Basket",  # Full name works too!
            season="2025"
        )

        print(f"✅ Successfully retrieved rosters for {len(rosters_by_name)} teams")
        print("✨ This should be identical to Method 1 results")

    except Exception as e:
        print(f"❌ Error with League Name method: {e}")

    # Method 3: Get individual team roster
    print("\n\n📋 Method 3: Individual Team Roster")
    print("-" * 38)

    try:
        # First, let's get the teams in the league
        teams = api.get_teams_from_teams_page(league_id=None, league_name="Italian-Serie-A2-Basket")

        if teams:
            # Pick the first team as an example
            example_team = teams[0]
            print(f"Getting detailed roster for: {example_team['name']}")

            team_roster = api.get_team_roster(
                league=54,  # Using the new resolver system
                team_id=example_team['id'],
                team_name=example_team['name_slug'],
                season="2025"
            )

            print(f"\n🏀 {team_roster.get('team_name', 'Unknown Team')} Detailed Roster:")
            print(f"📅 Season: {team_roster.get('season', 'N/A')}")

            if 'roster' in team_roster:
                players = team_roster['roster']
                print(f"📊 Total Players: {len(players)}")
                print("\nPlayer Details:")
                print("-" * 60)

                for i, player in enumerate(players, 1):
                    name = player.get('name', 'Unknown')
                    number = player.get('number', 'N/A')
                    position = player.get('position', 'N/A')
                    height = player.get('height_imperial', 'N/A')
                    weight = player.get('weight_imperial', 'N/A')
                    experience = player.get('experience', 'N/A')

                    print(f"{i:2d}. #{number:<3} {name:<25} {position:<3} {height:<8} {weight:<8} {experience}")

    except Exception as e:
        print(f"❌ Error with individual team method: {e}")

    # Method 4: Save rosters to JSON file
    print("\n\n📋 Method 4: Save All Rosters to File")
    print("-" * 40)

    try:
        output_file = f"italian_serie_a2_rosters_{datetime.now().strftime('%Y%m%d')}.json"

        print(f"Saving all rosters to: {output_file}")

        # Get rosters and save to file
        all_rosters = api.get_league_rosters(
            league=54,
            season="2025",
            output_file=output_file  # This will save automatically
        )

        print(f"✅ Rosters saved to {output_file}")
        print(f"📊 Total teams: {len(all_rosters)}")

        # Also demonstrate manual saving
        manual_file = f"manual_rosters_{datetime.now().strftime('%Y%m%d')}.json"
        with open(manual_file, 'w', encoding='utf-8') as f:
            json.dump(all_rosters, f, indent=2, ensure_ascii=False)

        print(f"✅ Also saved manually to {manual_file}")

    except Exception as e:
        print(f"❌ Error saving rosters: {e}")

    # Method 5: Compare with old API (backward compatibility)
    print("\n\n📋 Method 5: Backward Compatibility Test")
    print("-" * 42)

    try:
        print("Testing old API parameters (should show deprecation warning)...")

        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Old way - should still work but show deprecation warning
            old_way_rosters = api.get_league_rosters(
                league_id=54,
                league_name="Italian-Serie-A2-Basket",
                season="2025"
            )

            if w:
                print(f"⚠️  Deprecation warning shown: {w[0].message}")

            print(f"✅ Old way still works: {len(old_way_rosters)} teams")
            print("💡 But please use the new 'league' parameter instead!")

    except Exception as e:
        print(f"❌ Error with backward compatibility: {e}")

    print("\n" + "=" * 50)
    print("🎯 Key Takeaways:")
    print("  • Use league=54 OR league='Italian Serie A2 Basket'")
    print("  • New resolver system is much cleaner and more flexible")
    print("  • Backward compatibility maintained with deprecation warnings")
    print("  • Can save rosters directly to JSON files")
    print("  • Works with both individual teams and entire leagues")


if __name__ == "__main__":
    main()