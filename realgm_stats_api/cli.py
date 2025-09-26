"""
Command Line Interface for RealGM Stats API
"""

import argparse
import sys
from typing import Optional
from .api import RealGMStatsAPI, STAT_TYPES, POSITIONS, PROSPECTS


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RealGM Basketball Statistics API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get Romanian Divizia A stats
  realgm-stats --league-id 31 --league-name "Romanian-Divizia-A"
  
  # Get stats for point guards only
  realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --position PG
  
  # Get totals instead of averages
  realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --stat-type Totals
  
  # Export to CSV
  realgm-stats --league-id 31 --league-name "Romanian-Divizia-A" --output stats.csv
  
  # Get depth chart for a specific team
  realgm-stats --league-id 62 --league-name "Puerto-Rican-BSN" --team-id 327 --team-name "Mets-de-Guaynabo" --depth-chart
  
  # Get depth charts for all teams in a league
  realgm-stats --league-id 62 --league-name "Puerto-Rican-BSN" --all-depth-charts --output depth_charts.json
  
  # Get depth charts for all teams using teams page and auto-save
  realgm-stats --league-id 15 --league-name "German-BBL" --league-depth-charts
  
  # List all teams from the teams page
  realgm-stats --league-id 15 --league-name "German-BBL" --list-league-teams
  
  # Get roster for a specific team
  realgm-stats --league-id 15 --league-name "German-BBL" --team-id 142 --team-name "ALBA-Berlin" --roster
  
  # Get rosters for all teams using teams page and auto-save
  realgm-stats --league-id 15 --league-name "German-BBL" --league-rosters
  
  # Get player profile only
  realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player-profile
  
  # Get complete player data for specific leagues
  realgm-stats --player-id 80999 --player-name "Elijah-Stewart" --player --leagues "International,NBA"
  
  # Get WNBA player stats
  realgm-stats --player-id 3000070 --player-name "Allisha-Gray" --player --leagues "WNBA"
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--league-id", 
        type=int, 
        default=31,
        help="League ID (default: 31 for Romanian Divizia A)"
    )
    parser.add_argument(
        "--league-name", 
        type=str, 
        default="Romanian-Divizia-A",
        help="League name slug (default: Romanian-Divizia-A)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--season", 
        type=str, 
        default="2025",
        help="Season year (default: 2025 for 2024-2025 season)"
    )
    parser.add_argument(
        "--stat-type", 
        choices=STAT_TYPES, 
        default="Averages",
        help="Type of statistics to retrieve"
    )
    parser.add_argument(
        "--position", 
        choices=POSITIONS, 
        default="All",
        help="Filter by player position"
    )
    parser.add_argument(
        "--prospects", 
        choices=PROSPECTS, 
        default="All",
        help="Filter by prospect type"
    )
    parser.add_argument(
        "--qualified", 
        action="store_true", 
        default=True,
        help="Show only qualified players"
    )
    parser.add_argument(
        "--no-qualified", 
        action="store_true",
        help="Show all players (including non-qualified)"
    )
    parser.add_argument(
        "--team", 
        type=str, 
        default="All",
        help="Filter by specific team"
    )
    parser.add_argument(
        "--sort-column", 
        type=str, 
        default="points",
        help="Column to sort by (default: points)"
    )
    parser.add_argument(
        "--sort-order", 
        choices=["desc", "asc"], 
        default="desc",
        help="Sort order"
    )
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file path (CSV format)"
    )
    parser.add_argument(
        "--format", 
        choices=["table", "csv", "json"], 
        default="table",
        help="Output format"
    )
    parser.add_argument(
        "--limit", 
        type=int,
        help="Limit number of results"
    )
    
    # Team-specific arguments for depth charts
    parser.add_argument(
        "--team-id", 
        type=int,
        help="Team ID for depth chart queries"
    )
    parser.add_argument(
        "--team-name", 
        type=str,
        help="Team name slug for depth chart queries"
    )
    
    # Actions
    parser.add_argument(
        "--list-teams", 
        action="store_true",
        help="List all teams in the league"
    )
    parser.add_argument(
        "--list-filters", 
        action="store_true",
        help="List all available filter options"
    )
    parser.add_argument(
        "--depth-chart", 
        action="store_true",
        help="Get depth chart for a specific team (requires --team-id and --team-name)"
    )
    parser.add_argument(
        "--all-depth-charts", 
        action="store_true",
        help="Get depth charts for all teams in the league"
    )
    parser.add_argument(
        "--league-depth-charts", 
        action="store_true",
        help="Get depth charts for all teams in the league and save to file (uses teams page)"
    )
    parser.add_argument(
        "--list-league-teams", 
        action="store_true",
        help="List all teams in the league from the teams page"
    )
    parser.add_argument(
        "--roster", 
        action="store_true",
        help="Get roster for a specific team (requires --team-id and --team-name)"
    )
    parser.add_argument(
        "--league-rosters", 
        action="store_true",
        help="Get rosters for all teams in the league and save to file (uses teams page)"
    )
    
    # Player-specific arguments
    parser.add_argument(
        "--player-id", 
        type=str,
        help="Player ID for player queries"
    )
    parser.add_argument(
        "--player-name", 
        type=str,
        help="Player name slug for player queries (e.g., 'Elijah-Stewart')"
    )
    parser.add_argument(
        "--leagues", 
        type=str,
        default="International",
        help="Comma-separated list of leagues for player stats (default: International). Options: International,NBA,WNBA,D-League,NCAA"
    )
    
    # Player actions
    parser.add_argument(
        "--player-profile", 
        action="store_true",
        help="Get player profile information only (requires --player-id and --player-name)"
    )
    parser.add_argument(
        "--player", 
        action="store_true",
        help="Get complete player information including profile and stats (requires --player-id and --player-name)"
    )
    
    # League players arguments
    parser.add_argument(
        "--league-players", 
        action="store_true",
        help="Get all players in a league (NBA, WNBA only)"
    )
    parser.add_argument(
        "--players-team", 
        type=str,
        help="Team filter for league players (e.g., 'Chicago-Sky', 'Atlanta Hawks')"
    )
    
    args = parser.parse_args()
    
    # Handle qualified flag
    if args.no_qualified:
        qualified = False
    else:
        qualified = args.qualified
    
    try:
        api = RealGMStatsAPI()
        
        if args.list_teams:
            teams = api.get_team_list(args.league_id, args.league_name, args.season)
            print(f"Teams in {args.league_name} ({args.season} season):")
            for team in teams:
                print(f"  {team['name']} (ID: {team['id']})")
            return
        
        if args.list_filters:
            filters = api.get_available_filters(args.league_id, args.league_name)
            print(f"Available filters for {args.league_name}:")
            for filter_name, options in filters.items():
                print(f"\n{filter_name}:")
                for option in options[:10]:  # Show first 10 options
                    print(f"  {option['text']}")
                if len(options) > 10:
                    print(f"  ... and {len(options) - 10} more")
            return
        
        # Handle depth chart commands
        if args.depth_chart:
            if not args.team_id or not args.team_name:
                print("Error: --depth-chart requires both --team-id and --team-name", file=sys.stderr)
                sys.exit(1)
            
            print(f"Fetching depth chart for team {args.team_name} in {args.league_name}...")
            depth_chart = api.get_depth_chart(
                league_id=args.league_id,
                league_name=args.league_name,
                team_id=args.team_id,
                team_name=args.team_name,
                season=args.season
            )
            
            if args.output:
                if args.output.endswith('.json'):
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(depth_chart, f, indent=2)
                    print(f"Depth chart saved to {args.output}")
                else:
                    print("Error: Depth chart output must be JSON format", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "json":
                    import json
                    print(json.dumps(depth_chart, indent=2))
                else:
                    print(f"\nDepth Chart for {depth_chart['team_name']} ({args.season} season)")
                    print("=" * 50)
                    
                    # Print depth chart structure
                    for role, positions in depth_chart['depth_chart'].items():
                        print(f"\n{role.upper().replace('_', ' ')}:")
                        for pos, player in positions.items():
                            if player:
                                stats_str = ""
                                if 'season_stats' in player:
                                    stats = player['season_stats']
                                    stats_parts = []
                                    if 'points' in stats:
                                        stats_parts.append(f"{stats['points']}p")
                                    if 'rebounds' in stats:
                                        stats_parts.append(f"{stats['rebounds']}r")
                                    if 'assists' in stats:
                                        stats_parts.append(f"{stats['assists']}a")
                                    stats_str = f" ({' '.join(stats_parts)})" if stats_parts else ""
                                print(f"  {pos}: {player['name']}{stats_str}")
                    
                    # Print team leaders if available
                    if depth_chart['team_leaders']:
                        print(f"\nTEAM LEADERS:")
                        for stat, leader in depth_chart['team_leaders'].items():
                            print(f"  {stat}: {leader['player_name']} ({leader['value']})")
            return
        
        if args.all_depth_charts:
            print(f"Fetching depth charts for all teams in {args.league_name}...")
            depth_charts = api.get_team_depth_charts(
                league_id=args.league_id,
                league_name=args.league_name,
                season=args.season
            )
            
            if args.output:
                if args.output.endswith('.json'):
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(depth_charts, f, indent=2)
                    print(f"All depth charts saved to {args.output}")
                else:
                    print("Error: Depth charts output must be JSON format", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "json":
                    import json
                    print(json.dumps(depth_charts, indent=2))
                else:
                    print(f"\nDepth Charts for {args.league_name} ({args.season} season)")
                    print("=" * 60)
                    
                    for team_name, depth_chart in depth_charts.items():
                        print(f"\n{team_name.upper()}:")
                        print("-" * 40)
                        
                        for role, positions in depth_chart['depth_chart'].items():
                            print(f"\n{role.upper().replace('_', ' ')}:")
                            for pos, player in positions.items():
                                if player:
                                    stats_str = ""
                                    if 'season_stats' in player:
                                        stats = player['season_stats']
                                        stats_parts = []
                                        if 'points' in stats:
                                            stats_parts.append(f"{stats['points']}p")
                                        if 'rebounds' in stats:
                                            stats_parts.append(f"{stats['rebounds']}r")
                                        if 'assists' in stats:
                                            stats_parts.append(f"{stats['assists']}a")
                                        stats_str = f" ({' '.join(stats_parts)})" if stats_parts else ""
                                    print(f"  {pos}: {player['name']}{stats_str}")
            return
        
        if args.league_depth_charts:
            print(f"Fetching depth charts for all teams in {args.league_name} and saving to file...")
            output_file = args.output if args.output else f"{args.league_name.lower().replace('-', '_')}_depth_charts.json"
            
            depth_charts = api.get_league_depth_charts(
                league_id=args.league_id,
                league_name=args.league_name,
                season=args.season,
                output_file=output_file
            )
            
            if not args.output:
                print(f"Depth charts automatically saved to {output_file}")
            
            if args.format == "json":
                import json
                print(json.dumps(depth_charts, indent=2))
            else:
                print(f"\nLeague Depth Charts Summary for {args.league_name} ({args.season} season)")
                print("=" * 70)
                print(f"Total teams: {depth_charts['total_teams']}")
                print(f"Successfully scraped: {len([t for t in depth_charts['teams'].values() if 'error' not in t])}")
                print(f"Errors: {len([t for t in depth_charts['teams'].values() if 'error' in t])}")
                
                print(f"\nTeams with depth charts:")
                for team_name, depth_chart in depth_charts['teams'].items():
                    if 'error' not in depth_chart:
                        print(f"  ✅ {team_name}")
                    else:
                        print(f"  ❌ {team_name} - {depth_chart['error']}")
            return
        
        if args.list_league_teams:
            teams = api.get_teams_from_teams_page(args.league_id, args.league_name)
            print(f"Teams in {args.league_name} from teams page:")
            for team in teams:
                print(f"  {team['name']} (ID: {team['id']}, Slug: {team['name_slug']})")
            return
        
        # Handle roster commands
        if args.roster:
            if not args.team_id or not args.team_name:
                print("Error: --roster requires both --team-id and --team-name", file=sys.stderr)
                sys.exit(1)
            
            print(f"Fetching roster for team {args.team_name} in {args.league_name}...")
            roster = api.get_team_roster(
                league_id=args.league_id,
                league_name=args.league_name,
                team_id=args.team_id,
                team_name=args.team_name,
                season=args.season
            )
            
            if args.output:
                if args.output.endswith('.json'):
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(roster, f, indent=2)
                    print(f"Roster saved to {args.output}")
                else:
                    print("Error: Roster output must be JSON format", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "json":
                    import json
                    print(json.dumps(roster, indent=2))
                else:
                    print(f"\nRoster for {roster['team_name']} ({args.season} season)")
                    print("=" * 50)
                    print(f"Total players: {len(roster['roster'])}")
                    
                    # Print roster table
                    if roster['roster']:
                        print(f"\n{'#':<4} {'Player':<25} {'Pos':<4} {'Height':<8} {'Weight':<6} {'Age':<4} {'Birth City':<20}")
                        print("-" * 90)
                        for player in roster['roster']:
                            number = str(player.get('number', '-')) if player.get('number') is not None else '-'
                            name = str(player.get('name', '-'))[:24]
                            position = str(player.get('position', '-'))
                            height = str(player.get('height', '-'))
                            weight = str(player.get('weight', '-'))
                            age = str(player.get('age', '-')) if player.get('age') is not None else '-'
                            birth_city = str(player.get('birth_city', '-') or '-')[:19]
                            print(f"{number:<4} {name:<25} {position:<4} {height:<8} {weight:<6} {age:<4} {birth_city:<20}")
            return
        
        if args.league_rosters:
            print(f"Fetching rosters for all teams in {args.league_name} and saving to file...")
            output_file = args.output if args.output else f"{args.league_name.lower().replace('-', '_')}_rosters.json"
            
            rosters = api.get_league_rosters(
                league_id=args.league_id,
                league_name=args.league_name,
                season=args.season,
                output_file=output_file
            )
            
            if not args.output:
                print(f"Rosters automatically saved to {output_file}")
            
            if args.format == "json":
                import json
                print(json.dumps(rosters, indent=2))
            else:
                print(f"\nLeague Rosters Summary for {args.league_name} ({args.season} season)")
                print("=" * 70)
                print(f"Total teams: {rosters['total_teams']}")
                print(f"Successfully scraped: {len([t for t in rosters['teams'].values() if 'error' not in t])}")
                print(f"Errors: {len([t for t in rosters['teams'].values() if 'error' in t])}")
                
                print(f"\nTeams with rosters:")
                for team_name, roster in rosters['teams'].items():
                    if 'error' not in roster:
                        player_count = len(roster.get('roster', []))
                        print(f"  ✅ {team_name} ({player_count} players)")
                    else:
                        print(f"  ❌ {team_name} - {roster['error']}")
            return
        
        # Handle player commands
        if args.player_profile:
            if not args.player_id or not args.player_name:
                print("Error: --player-profile requires both --player-id and --player-name", file=sys.stderr)
                sys.exit(1)
            
            print(f"Fetching profile for player {args.player_name}...")
            profile = api.get_player_profile(args.player_id, args.player_name)
            
            if args.output:
                if args.output.endswith('.json'):
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(profile, f, indent=2)
                    print(f"Player profile saved to {args.output}")
                else:
                    print("Error: Player profile output must be JSON format", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "json":
                    import json
                    print(json.dumps(profile, indent=2))
                else:
                    print(f"\nPlayer Profile: {profile.get('name', args.player_name.replace('-', ' '))}")
                    print("=" * 50)
                    print(f"Position: {profile.get('position', 'N/A')}")
                    if profile.get('jersey'):
                        print(f"Jersey: {profile['jersey']}")
                    print(f"Height: {profile.get('height_imperial', 'N/A')} ({profile.get('height_metric', 'N/A')}cm)")
                    print(f"Weight: {profile.get('weight_imperial', 'N/A')} ({profile.get('weight_metric', 'N/A')}kg)")
                    print(f"Born: {profile.get('date_of_birth', 'N/A')} ({profile.get('age', 'N/A')})")
                    print(f"Hometown: {profile.get('hometown', 'N/A')}")
                    print(f"Nationality: {profile.get('nationality', 'N/A')}")
            return
        
        if args.player:
            if not args.player_id or not args.player_name:
                print("Error: --player requires both --player-id and --player-name", file=sys.stderr)
                sys.exit(1)
            
            # Parse leagues argument
            leagues = [league.strip() for league in args.leagues.split(',')]
            
            print(f"Fetching complete player data for {args.player_name} (leagues: {', '.join(leagues)})...")
            player_data = api.get_player(args.player_id, args.player_name, leagues)
            
            if args.output:
                if args.output.endswith('.json'):
                    import json
                    # Convert DataFrames to dict for JSON serialization
                    output_data = {
                        'player_id': player_data['player_id'],
                        'name': player_data['name'],
                        'profile': player_data['profile'],
                        'stats': {}
                    }
                    for league, df in player_data['stats'].items():
                        output_data['stats'][league] = df.to_dict('records')
                    
                    with open(args.output, 'w') as f:
                        json.dump(output_data, f, indent=2)
                    print(f"Player data saved to {args.output}")
                else:
                    print("Error: Player data output must be JSON format", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "json":
                    import json
                    # Convert DataFrames to dict for JSON serialization
                    output_data = {
                        'player_id': player_data['player_id'],
                        'name': player_data['name'],
                        'profile': player_data['profile'],
                        'stats': {}
                    }
                    for league, df in player_data['stats'].items():
                        output_data['stats'][league] = df.to_dict('records')
                    
                    print(json.dumps(output_data, indent=2))
                else:
                    print(f"\nPlayer: {player_data['name']} (ID: {player_data['player_id']})")
                    print("=" * 60)
                    
                    # Print profile
                    profile = player_data['profile']
                    print(f"\nPROFILE:")
                    print(f"Position: {profile.get('position', 'N/A')}")
                    if profile.get('jersey'):
                        print(f"Jersey: {profile['jersey']}")
                    print(f"Height: {profile.get('height_imperial', 'N/A')} ({profile.get('height_metric', 'N/A')}cm)")
                    print(f"Weight: {profile.get('weight_imperial', 'N/A')} ({profile.get('weight_metric', 'N/A')}kg)")
                    print(f"Born: {profile.get('date_of_birth', 'N/A')} ({profile.get('age', 'N/A')})")
                    print(f"Hometown: {profile.get('hometown', 'N/A')}")
                    print(f"Nationality: {profile.get('nationality', 'N/A')}")
                    
                    # Print stats for each league
                    for league, df in player_data['stats'].items():
                        if not df.empty:
                            print(f"\n{league.upper()} STATS:")
                            print("-" * 40)
                            print(df.to_string(index=False))
                        else:
                            print(f"\n{league.upper()} STATS: No data available")
            return
        
        # Handle league players command
        if args.league_players:
            if not args.league_name or args.league_name.lower() not in ['nba', 'wnba']:
                print("Error: --league-players requires --league-name to be 'nba' or 'wnba'", file=sys.stderr)
                sys.exit(1)
            
            print(f"Fetching all players in {args.league_name.upper()} for {args.season}...")
            if args.players_team:
                print(f"Filtering by team: {args.players_team}")
            
            players_df = api.get_league_players(
                league_name=args.league_name.upper(),
                season=args.season,
                team=args.players_team
            )
            
            if args.output:
                if args.output.endswith('.csv'):
                    players_df.to_csv(args.output, index=False)
                    print(f"Players data saved to {args.output}")
                elif args.output.endswith('.json'):
                    players_df.to_json(args.output, orient='records', indent=2)
                    print(f"Players data saved to {args.output}")
                else:
                    print("Error: Output file must have .csv or .json extension", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.format == "csv":
                    print(players_df.to_csv(index=False))
                elif args.format == "json":
                    print(players_df.to_json(orient='records', indent=2))
                else:  # table format
                    print(f"\n{len(players_df)} players found in {args.league_name.upper()}")
                    if args.limit:
                        players_df = players_df.head(args.limit)
                    print(players_df.to_string(index=False, max_rows=20))
                    if len(players_df) > 20:
                        print(f"\n... and {len(players_df) - 20} more players")
                        print("Use --limit or --output to get all results")
            return
        
        # Get stats
        print(f"Fetching {args.stat_type} stats for {args.league_name}...")
        
        df = api.get_league_stats(
            league_id=args.league_id,
            league_name=args.league_name,
            season=args.season,
            stat_type=args.stat_type,
            qualified=qualified,
            prospects=args.prospects,
            team=args.team,
            position=args.position,
            sort_column=args.sort_column,
            sort_order=args.sort_order
        )
        
        if args.limit:
            df = df.head(args.limit)
        
        # Output results
        if args.output:
            if args.output.endswith('.csv'):
                df.to_csv(args.output, index=False)
                print(f"Data saved to {args.output}")
            elif args.output.endswith('.json'):
                df.to_json(args.output, orient='records', indent=2)
                print(f"Data saved to {args.output}")
            else:
                print("Error: Output file must have .csv or .json extension")
                sys.exit(1)
        else:
            if args.format == "csv":
                print(df.to_csv(index=False))
            elif args.format == "json":
                print(df.to_json(orient='records', indent=2))
            else:  # table format
                print(f"\n{len(df)} players found")
                print(df.to_string(index=False, max_rows=20))
                if len(df) > 20:
                    print(f"\n... and {len(df) - 20} more players")
                    print("Use --limit or --output to get all results")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
