from realgm_stats_api import RealGMStatsAPI, get_league_id_by_name
import pandas as pd
from datetime import datetime

def print_stats(df: pd.DataFrame, title: str):
    """Helper function to print stats with a title"""
    print(f"\n=== {title} ===")
    print(df)
    print("\n")

def main():
    # Initialize API
    api = RealGMStatsAPI()
    
    # Find league by exact name
    league_name = "French Jeep Elite"  # Example: Czech NBL
    league_id = get_league_id_by_name(league_name)
    if not league_id:
        print(f"Could not find league: {league_name}")
        return
    
    print(f"Found league: {league_name} (ID: {league_id})")
    
    # Example 1: Get basic averages
    print("\n1. Getting basic averages...")
    basic_stats = api.get_league_stats(
        league_id=league_id,
        league_name=league_name,
        season="2025",
        stat_type="Averages",
        qualified=True,
        position="All"
    )
    print_stats(basic_stats, "Basic Averages")
    
    # Example 2: Get advanced stats
    print("\n2. Getting advanced stats...")
    advanced_stats = api.get_league_stats(
        league_id=league_id,
        league_name=league_name,
        season="2025",
        stat_type="Advanced_Stats",
        qualified=True,
        position="All",
        sort_column="points",
        sort_order="desc"
    )
    print_stats(advanced_stats, "Advanced Stats")
    
    # Example 3: Get stats for point guards only
    print("\n3. Getting point guard stats...")
    pg_stats = api.get_league_stats(
        league_id=league_id,
        league_name=league_name,
        season="2025",
        stat_type="Averages",
        qualified=True,
        position="PG",
        sort_column="assists",
        sort_order="desc"
    )
    print_stats(pg_stats, "Point Guard Stats")
    
    # Example 4: Get all stats
    print("\n4. Getting multiple stats...")
    multiple_stats = api.get_league_stats(
        league_id=league_id,
        league_name=league_name,
        season="2025",
        stat_type=["Totals", "Misc_Stats", "Advanced_Stats"],
        qualified=True,
        position="All",
        sort_column="points",
        sort_order="desc"
    )
    print_stats(multiple_stats, "Multiple Stats")

if __name__ == "__main__":
    main() 