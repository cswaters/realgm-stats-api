# Examples

This directory contains example scripts demonstrating various features of the RealGM Stats API.

## Basic Usage Examples

- `example_get_league_stats.py` - Get player statistics for a league
- `example_all_leagues.py` - List all available leagues
- `example_major_leagues.py` - Work with NBA/WNBA data
- `example_rosters.py` - Get team rosters
- `example_depth_charts.py` - Get team depth charts
- `example_league_depth_charts.py` - Get depth charts for entire league
- `example_upcoming_games.py` - Get upcoming game schedules

## Boxscore Examples

- `example_boxscores.py` - Download and parse game boxscores
- `download_boxscores.py` - Bulk download boxscores for a date range

## WNBA-Specific Examples

- `download_wnba_rosters.py` - Download WNBA team rosters
- `download_wnba_team_stats.py` - Download WNBA team statistics

## Debug/Development Examples

- `example_debug.py` - Basic debugging script
- `example_debug_get_teams.py` - Debug team fetching
- `example_debug_roster.py` - Debug roster fetching
- `example_team_scraper.py` - Team scraping utilities

## Usage

Run any example script from the project root:

```bash
python examples/example_get_league_stats.py
```

Make sure you have the package installed:

```bash
pip install -e .
```