"""
RealGM Basketball Stats API
A Python package to scrape and filter RealGM basketball statistics
"""

from .api import RealGMStatsAPI, create_api_client, STAT_TYPES, POSITIONS, PROSPECTS
from .leagues import get_league_by_id, get_league_id_by_name, find_league_by_regex, search_leagues
from .boxscore import BoxscoreScraper
from .player import PlayerScraper

__version__ = "0.1.0"
__author__ = "Cory Waters"
__email__ = "corywaters@gmail.com"

__all__ = [
    "RealGMStatsAPI",
    "create_api_client", 
    "STAT_TYPES",
    "POSITIONS", 
    "PROSPECTS",
    "get_league_by_id",
    "get_league_id_by_name",
    "find_league_by_regex",
    "search_leagues",
    "BoxscoreScraper",
    "PlayerScraper"
]
 