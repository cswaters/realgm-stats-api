"""
Resolvers for smart ID/name handling across the API.

This module provides resolver classes that can automatically detect whether
an input is an ID, name, or slug and resolve it to all needed formats.
"""

import re
from typing import Dict, Optional, Union, Any
from .leagues import BASKETBALL_LEAGUES, get_league_by_id, get_league_id_by_name, search_leagues


class LeagueResolver:
    """
    Smart resolver for league identifiers.

    Accepts league ID (int), name (str), or slug (str) and resolves to all formats.
    Includes caching for performance.
    """

    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, league_input: Union[int, str, None] = None):
        self.input = league_input
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.slug: Optional[str] = None
        self.is_major: bool = False

        if league_input is not None:
            self._resolve()

    def _resolve(self):
        """Resolve the input to all needed formats."""
        cache_key = str(self.input)

        # Check cache first
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            self.id = cached['id']
            self.name = cached['name']
            self.slug = cached['slug']
            self.is_major = cached['is_major']
            return

        # Auto-detect input type and resolve
        if isinstance(self.input, int):
            self._resolve_from_id(self.input)
        elif isinstance(self.input, str):
            # Try to parse as integer first
            if self.input.isdigit():
                self._resolve_from_id(int(self.input))
            else:
                self._resolve_from_string(self.input)
        else:
            raise ValueError(f"Invalid league input: {self.input}")

        # Cache the result
        self._cache[cache_key] = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'is_major': self.is_major
        }

    def _resolve_from_id(self, league_id: int):
        """Resolve from league ID."""
        self.id = league_id
        self.name = get_league_by_id(league_id)

        if self.name is None:
            raise ValueError(f"Unknown league ID: {league_id}")

        self.slug = self._generate_slug(self.name)
        self.is_major = self._is_major_league(self.name)

    def _resolve_from_string(self, league_str: str):
        """Resolve from league name or slug."""
        # Check for major leagues first (case insensitive)
        if league_str.lower() in ['nba', 'wnba']:
            self.slug = league_str.lower()
            self.name = league_str.upper()
            self.id = 163 if league_str.lower() == 'nba' else 164
            self.is_major = True
            return

        # Try exact name match first
        league_id = get_league_id_by_name(league_str, exact_match=True)
        if league_id:
            self.id = league_id
            self.name = league_str
            self.slug = self._generate_slug(league_str)
            self.is_major = self._is_major_league(league_str)
            return

        # Try fuzzy search
        matches = search_leagues(league_str)
        if matches:
            # Use the first match
            self.id, self.name = matches[0]
            self.slug = self._generate_slug(self.name)
            self.is_major = self._is_major_league(self.name)
            return

        # Try as slug - convert slug to name and search
        potential_name = league_str.replace('-', ' ')
        matches = search_leagues(potential_name)
        if matches:
            self.id, self.name = matches[0]
            self.slug = league_str  # Use provided slug
            self.is_major = self._is_major_league(self.name)
            return

        raise ValueError(f"Could not resolve league: {league_str}")

    def _generate_slug(self, name: str) -> str:
        """Generate URL slug from league name."""
        if self.is_major:
            return name.lower()

        # For international leagues, use RealGM's slug format
        return name.replace(' ', '-')

    def _is_major_league(self, name: str) -> bool:
        """Check if this is a major league (NBA/WNBA)."""
        return name.upper() in ['NBA', 'WNBA']

    def __str__(self):
        return f"LeagueResolver(id={self.id}, name='{self.name}', slug='{self.slug}')"

    def __repr__(self):
        return self.__str__()


class TeamResolver:
    """
    Smart resolver for team identifiers within a league.

    Accepts team ID (int), name (str), or slug (str) and resolves to all formats.
    Requires a LeagueResolver for context.
    """

    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, team_input: Union[int, str, None] = None, league_resolver: LeagueResolver = None):
        self.input = team_input
        self.league = league_resolver
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.slug: Optional[str] = None

        if team_input is not None and league_resolver is not None:
            self._resolve()

    def _resolve(self):
        """Resolve the team input to all needed formats."""
        if self.league is None:
            raise ValueError("League resolver is required for team resolution")

        cache_key = f"{self.league.id}:{self.input}"

        # Check cache first
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            self.id = cached['id']
            self.name = cached['name']
            self.slug = cached['slug']
            return

        # Handle special case for "All"
        if isinstance(self.input, str) and self.input.lower() == "all":
            self.id = None
            self.name = "All"
            self.slug = "All"
            return

        # Auto-detect input type and resolve
        if isinstance(self.input, int):
            self._resolve_from_id(self.input)
        elif isinstance(self.input, str):
            if self.input.isdigit():
                self._resolve_from_id(int(self.input))
            else:
                self._resolve_from_string(self.input)
        else:
            raise ValueError(f"Invalid team input: {self.input}")

        # Cache the result
        self._cache[cache_key] = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug
        }

    def _resolve_from_id(self, team_id: int):
        """Resolve from team ID - requires API call."""
        # This would need to query the API to get team info
        # For now, set basics and slug will be generated later
        self.id = team_id
        self.name = f"Team-{team_id}"  # Placeholder
        self.slug = f"Team-{team_id}"  # Placeholder

    def _resolve_from_string(self, team_str: str):
        """Resolve from team name or slug."""
        # Handle hardcoded major league teams
        if self.league.is_major and self.league.slug == "wnba":
            wnba_teams = {
                "Atlanta Dream": {"id": 1, "slug": "Atlanta-Dream"},
                "Chicago Sky": {"id": 3, "slug": "Chicago-Sky"},
                "Connecticut Sun": {"id": 5, "slug": "Connecticut-Sun"},
                "Dallas Wings": {"id": 6, "slug": "Dallas-Wings"},
                "Golden State Valkyries": {"id": 7, "slug": "Golden-State-Valkyries"},
                "Indiana Fever": {"id": 9, "slug": "Indiana-Fever"},
                "Los Angeles Sparks": {"id": 10, "slug": "Los-Angeles-Sparks"},
                "Las Vegas Aces": {"id": 11, "slug": "Las-Vegas-Aces"},
                "Seattle Storm": {"id": 18, "slug": "Seattle-Storm"},
                "Washington Mystics": {"id": 19, "slug": "Washington-Mystics"},
                "Minnesota Lynx": {"id": 13, "slug": "Minnesota-Lynx"},
                "New York Liberty": {"id": 14, "slug": "New-York-Liberty"},
                "Phoenix Mercury": {"id": 15, "slug": "Phoenix-Mercury"}
            }

            # Try exact name match
            if team_str in wnba_teams:
                self.name = team_str
                self.id = wnba_teams[team_str]["id"]
                self.slug = wnba_teams[team_str]["slug"]
                return

            # Try slug match
            for name, info in wnba_teams.items():
                if info["slug"] == team_str or info["slug"].replace('-', ' ') == team_str:
                    self.name = name
                    self.id = info["id"]
                    self.slug = info["slug"]
                    return

        # For other leagues, generate slug from name
        self.name = team_str
        self.slug = team_str.replace(' ', '-')
        self.id = None  # Would need API call to get ID

    def __str__(self):
        return f"TeamResolver(id={self.id}, name='{self.name}', slug='{self.slug}')"

    def __repr__(self):
        return self.__str__()


# Convenience functions
def resolve_league(league_input: Union[int, str, None]) -> LeagueResolver:
    """Convenience function to create a LeagueResolver."""
    return LeagueResolver(league_input)


def resolve_team(team_input: Union[int, str, None], league_resolver: LeagueResolver) -> TeamResolver:
    """Convenience function to create a TeamResolver."""
    return TeamResolver(team_input, league_resolver)