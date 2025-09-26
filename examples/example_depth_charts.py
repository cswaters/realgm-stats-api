#!/usr/bin/env python3
"""
Example script demonstrating depth chart functionality
"""

import json
from realgm_stats_api import RealGMStatsAPI


def main():
    """Demonstrate depth chart functionality"""
    
    # Initialize API client
    api = RealGMStatsAPI()
    
    # Example: Get depth chart for Mets de Guaynabo (Puerto Rican BSN)
    print("=== Depth Chart Example ===")
    print("Getting depth chart for Mets de Guaynabo (Puerto Rican BSN)...")
    
    try:
        depth_chart = api.get_depth_chart(
            league_id=62,
            league_name="Puerto-Rican-BSN",
            team_id=327,
            team_name="Mets-de-Guaynabo",
            season="2025"
        )
        
        print(f"\nDepth Chart for {depth_chart['team_name']} ({depth_chart['season']} season)")
        print("=" * 60)
        
        # Display depth chart structure
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
        
        # Display team leaders
        if depth_chart['team_leaders']:
            print(f"\nTEAM LEADERS:")
            for stat, leader in depth_chart['team_leaders'].items():
                print(f"  {stat}: {leader['player_name']} ({leader['value']})")
        
        # Save to JSON file
        with open('mets_guaynabo_depth_chart.json', 'w') as f:
            json.dump(depth_chart, f, indent=2)
        print(f"\nDepth chart saved to mets_guaynabo_depth_chart.json")
        
    except Exception as e:
        print(f"Error getting depth chart: {e}")
    
    # Example: Get depth charts for all teams in Puerto Rican BSN
    print("\n\n=== All Teams Depth Charts Example ===")
    print("Getting depth charts for all teams in Puerto Rican BSN...")
    
    try:
        all_depth_charts = api.get_team_depth_charts(
            league_id=62,
            league_name="Puerto-Rican-BSN",
            season="2025"
        )
        
        print(f"\nFound depth charts for {len(all_depth_charts)} teams:")
        for team_name in all_depth_charts.keys():
            print(f"  - {team_name}")
        
        # Save to JSON file
        with open('puerto_rican_bsn_depth_charts.json', 'w') as f:
            json.dump(all_depth_charts, f, indent=2)
        print(f"\nAll depth charts saved to puerto_rican_bsn_depth_charts.json")
        
        # Show a sample depth chart structure
        if all_depth_charts:
            sample_team = list(all_depth_charts.keys())[0]
            sample_chart = all_depth_charts[sample_team]
            print(f"\nSample depth chart structure for {sample_team}:")
            print(f"  - League ID: {sample_chart['league_id']}")
            print(f"  - Season: {sample_chart['season']}")
            print(f"  - Depth chart roles: {list(sample_chart['depth_chart'].keys())}")
            print(f"  - Team leaders: {list(sample_chart['team_leaders'].keys())}")
        
    except Exception as e:
        print(f"Error getting all depth charts: {e}")


if __name__ == "__main__":
    main() 