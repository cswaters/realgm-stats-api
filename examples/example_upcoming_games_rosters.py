#!/usr/bin/env python3
"""
Real-World Example: Upcoming Games and Team Rosters

This example demonstrates the new resolver system by:
1. Finding upcoming games in League 54 (Italian Serie A2) in the next 5 days
2. Getting the rosters for teams that are playing in those games
"""

from realgm_stats_api import RealGMStatsAPI
from datetime import datetime, timedelta
import json
from collections import defaultdict


def main():
    # Initialize the API client
    api = RealGMStatsAPI()

    print("🏀 Real-World Example: Upcoming Games & Team Rosters")
    print("League 54: Italian Serie A2 Basket")
    print("=" * 60)

    # Step 1: Get the next 5 days of dates
    today = datetime.now()
    upcoming_dates = []
    for i in range(5):
        date = today + timedelta(days=i)
        upcoming_dates.append(date.strftime("%Y-%m-%d"))

    print(f"📅 Checking games for dates: {', '.join(upcoming_dates)}")

    # Step 2: Find all games in the next 5 days using the new resolver
    all_games = []
    teams_playing = set()

    for date in upcoming_dates:
        print(f"\n🔍 Checking {date}...")

        try:
            # Using the new resolver system - can use league ID or name
            # Use get_upcoming_games for future games, not get_boxscore_links (which is for completed games)
            games = api.get_upcoming_games(54, date, 'Italian-Serie-A2-Basket')

            if games:
                print(f"   Found {len(games)} games:")
                for game in games:
                    print(f"   • {game['away_team']} @ {game['home_team']}")

                    # Track teams that are playing
                    teams_playing.add(game['away_team'])
                    teams_playing.add(game['home_team'])

                    # Store game info
                    all_games.append({
                        'date': date,
                        'away_team': game['away_team'],
                        'home_team': game['home_team'],
                        'game_id': game['game_id']
                    })
            else:
                print("   No games found")

        except Exception as e:
            print(f"   ❌ Error checking {date}: {e}")

    print(f"\n📊 Summary:")
    print(f"   Total games found: {len(all_games)}")
    print(f"   Unique teams playing: {len(teams_playing)}")

    if not teams_playing:
        print("\n❌ No games found in the next 5 days. Cannot proceed with roster fetching.")
        return

    # Step 3: Get rosters for teams that are playing
    print(f"\n🏀 Getting rosters for teams playing in upcoming games...")
    print("-" * 50)

    team_rosters = {}
    successful_rosters = 0

    for i, team_name in enumerate(sorted(teams_playing), 1):
        print(f"[{i}/{len(teams_playing)}] Fetching roster for {team_name}...")

        try:
            # First, we need to get the team's ID and info from the league teams
            teams_info = api.get_teams_from_teams_page(
                league_id=None,
                league_name="Italian-Serie-A2-Basket"
            )

            # Find the matching team
            team_info = None
            for team in teams_info:
                # Try different matching strategies
                if (team['name'] == team_name or
                    team['name'].replace(' ', '-') == team_name.replace(' ', '-') or
                    team_name in team['name'] or team['name'] in team_name):
                    team_info = team
                    break

            if team_info:
                print(f"   ✅ Found team info: {team_info['name']} (ID: {team_info['id']})")

                # Get the roster using the new resolver system
                roster = api.get_team_roster(
                    league=54,  # Using new resolver - much cleaner!
                    team=team_info['id'],
                    season="2025"
                )

                if roster and 'roster' in roster and roster['roster']:
                    players = roster['roster']
                    team_rosters[team_name] = {
                        'team_info': team_info,
                        'roster': players,
                        'player_count': len(players)
                    }
                    successful_rosters += 1
                    print(f"   📋 Roster retrieved: {len(players)} players")

                    # Show a few key players
                    for j, player in enumerate(players[:3]):
                        name = player.get('name', 'Unknown')
                        position = player.get('position', 'N/A')
                        height = player.get('height_imperial', 'N/A')
                        print(f"      {j+1}. {name} ({position}) - {height}")

                    if len(players) > 3:
                        print(f"      ... and {len(players) - 3} more players")
                else:
                    print(f"   ⚠️  No roster data available")

            else:
                print(f"   ❌ Could not find team info for: {team_name}")

        except Exception as e:
            print(f"   ❌ Error getting roster for {team_name}: {e}")

    # Step 4: Summary and analysis
    print(f"\n📊 Final Results:")
    print("=" * 40)
    print(f"Upcoming games in next 5 days: {len(all_games)}")
    print(f"Teams with rosters retrieved: {successful_rosters}/{len(teams_playing)}")

    if team_rosters:
        print(f"\n🏀 Team Roster Summary:")
        for team_name, data in team_rosters.items():
            player_count = data['player_count']
            print(f"   • {team_name}: {player_count} players")

        # Show upcoming matchups with roster info
        print(f"\n🎯 Upcoming Matchups (with roster data):")
        print("-" * 40)

        for game in all_games:
            away_team = game['away_team']
            home_team = game['home_team']
            date = game['date']

            away_roster_size = team_rosters.get(away_team, {}).get('player_count', 'N/A')
            home_roster_size = team_rosters.get(home_team, {}).get('player_count', 'N/A')

            print(f"{date}: {away_team} ({away_roster_size} players) @ {home_team} ({home_roster_size} players)")

    # Step 5: Save results to file
    if team_rosters:
        output_file = f"upcoming_games_rosters_{datetime.now().strftime('%Y%m%d')}.json"

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'league': 'Italian Serie A2 Basket',
            'league_id': 54,
            'date_range': upcoming_dates,
            'upcoming_games': all_games,
            'team_rosters': team_rosters
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"\n❌ Error saving results: {e}")

    print(f"\n✨ Example completed successfully!")
    print("This demonstrates the new resolver system:")
    print("  • api.get_boxscore_links(league=54, date=date)")
    print("  • api.get_team_roster(league=54, team=team_id)")
    print("  • Much cleaner than the old league_id + league_name approach!")


if __name__ == "__main__":
    main()