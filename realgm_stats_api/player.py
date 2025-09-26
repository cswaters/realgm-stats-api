"""
Player Scraper for RealGM Basketball Stats API
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin
from datetime import datetime
import pandas as pd


# Supported leagues for player stats
SUPPORTED_LEAGUES = {
    "International": "International",
    "NBA": "NBA", 
    "WNBA": "WNBA",
    "D-League": "D-League",
    "NCAA": "NCAA"
}

# Leagues that support the players listing page
PLAYERS_LISTING_LEAGUES = {
    "NBA": "nba",
    "WNBA": "wnba"
}


class PlayerScraper:
    """Scraper for RealGM player data"""
    
    def __init__(self, session: requests.Session, base_url: str, rate_limit: float = 1.0):
        self.session = session
        self.base_url = base_url
        self.rate_limit = rate_limit
    
    def get_player_profile(self, player_id: str, player_name: str) -> Dict:
        """
        Get player profile information from the Summary page
        
        Args:
            player_id: Player ID from RealGM
            player_name: Player name slug (e.g., "Elijah-Stewart")
            
        Returns:
            Dictionary containing player profile information:
            {
                'name': str,
                'position': str,
                'jersey': Optional[str],
                'height_imperial': str,
                'height_metric': str,
                'weight_imperial': str,
                'weight_metric': str,
                'date_of_birth': str,
                'age': str,
                'hometown': str,
                'nationality': str
            }
        """
        url = urljoin(self.base_url, f"/player/{player_name}/Summary/{player_id}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.rate_limit)
            
            return self._parse_player_profile(response.text, player_id, player_name)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching player profile: {e}")
    
    def get_player_stats(self, player_id: str, player_name: str, league: str) -> pd.DataFrame:
        """
        Get player stats for a specific league
        
        Args:
            player_id: Player ID from RealGM
            player_name: Player name slug (e.g., "Elijah-Stewart")
            league: League name (International, NBA, WNBA, D-League, NCAA)
            
        Returns:
            pandas DataFrame containing player statistics for the specified league
        """
        if league not in SUPPORTED_LEAGUES:
            raise ValueError(f"Unsupported league: {league}. Supported leagues: {list(SUPPORTED_LEAGUES.keys())}")
        
        url = urljoin(self.base_url, f"/player/{player_name}/{league}/{player_id}/Career/By_Split")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.rate_limit)
            
            return self._parse_player_stats_table(response.text, league)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching player stats for {league}: {e}")
    
    def get_player_stats_by_leagues(self, player_id: str, player_name: str, 
                                   leagues: List[str] = ["International"]) -> Dict:
        """
        Get player stats for specified leagues only
        
        Args:
            player_id: Player ID from RealGM
            player_name: Player name slug (e.g., "Elijah-Stewart")
            leagues: List of leagues to fetch stats for (default: ["International"])
            
        Returns:
            Dictionary containing player profile and stats for requested leagues:
            {
                'player_id': str,
                'name': str,
                'profile': Dict,
                'stats': Dict[str, pd.DataFrame]
            }
        """
        # Validate leagues
        invalid_leagues = [league for league in leagues if league not in SUPPORTED_LEAGUES]
        if invalid_leagues:
            raise ValueError(f"Unsupported leagues: {invalid_leagues}. Supported leagues: {list(SUPPORTED_LEAGUES.keys())}")
        
        # Get player profile
        profile = self.get_player_profile(player_id, player_name)
        
        # Get stats for each requested league
        stats = {}
        for league in leagues:
            try:
                league_stats = self.get_player_stats(player_id, player_name, league)
                if not league_stats.empty:
                    stats[league] = league_stats
            except Exception as e:
                # Log error but continue with other leagues
                print(f"Warning: Could not fetch {league} stats for {player_name}: {e}")
        
        return {
            'player_id': player_id,
            'name': profile.get('name', player_name.replace('-', ' ')),
            'profile': profile,
            'stats': stats
        }
    
    def get_league_players(self, league_name: str, season: str = "2025", team: str = None) -> pd.DataFrame:
        """
        Get all players in a league from the players listing page
        
        Args:
            league_name: League name (NBA, WNBA)
            season: Season year (e.g., "2025", "2024")
            team: Optional team filter (e.g., "Chicago-Sky", "Atlanta Hawks")
            
        Returns:
            pandas DataFrame containing all players with columns:
            #, Player, Pos, HT, WT, Age, Current Team, YOS, Pre-Draft Team, Draft Status, Nationality
        """
        if league_name not in PLAYERS_LISTING_LEAGUES:
            raise ValueError(f"Players listing not supported for {league_name}. Supported leagues: {list(PLAYERS_LISTING_LEAGUES.keys())}")
        
        # Build URL based on filters
        league_slug = PLAYERS_LISTING_LEAGUES[league_name]
        if team:
            # URL encode team name for spaces
            team_encoded = team.replace(' ', '%20')
            url = urljoin(self.base_url, f"/{league_slug}/players/{season}/{team_encoded}")
        else:
            url = urljoin(self.base_url, f"/{league_slug}/players/{season}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.rate_limit)
            
            return self._parse_league_players_table(response.text)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching league players for {league_name}: {e}")
    
    def _parse_player_profile(self, html: str, player_id: str, player_name: str) -> Dict:
        """
        Parse the player profile HTML page
        
        Args:
            html: HTML content of the page
            player_id: Player ID
            player_name: Player name slug
            
        Returns:
            Dictionary containing parsed profile information
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the profile box
        profile_box = soup.find('div', class_='profile-box')
        if not profile_box:
            raise Exception("Could not find profile box on player page")
        
        profile = {
            'name': None,
            'position': None,
            'jersey': None,
            'height_imperial': None,
            'height_metric': None,
            'weight_imperial': None,
            'weight_metric': None,
            'date_of_birth': None,
            'age': None,
            'hometown': None,
            'nationality': None
        }
        
        # Parse the h2 header which contains name, position, and jersey
        h2 = profile_box.find('h2')
        if h2:
            h2_text = h2.get_text(strip=True)
            # Parse format: "Player Name Position | Jersey" or "Player Name Position" or with jersey attached
            parts = h2_text.split('|')
            name_pos_part = parts[0].strip()
            jersey_part = parts[1].strip() if len(parts) > 1 else None

            # Robust regex: match name up to first position code, then position combo, then optional jersey
            # Examples:
            #   "Elijah StewartSF#44" -> name: Elijah Stewart, position: SF, jersey: 44
            #   "Allisha GrayG" -> name: Allisha Gray, position: G
            #   "John DoeSF-G#12" -> name: John Doe, position: SF-G, jersey: 12
            #   "John DoeSF-G" -> name: John Doe, position: SF-G
            #   "John Doe" -> name: John Doe
            pos_codes = "PG|SG|SF|PF|C|G|F"
            pattern = rf"^(.*?)(?:({pos_codes}(?:-(?:{pos_codes}))*))?(?:#?(\d+))?$"
            match = re.match(pattern, name_pos_part)
            if match:
                name = match.group(1).strip()
                position = match.group(2)
                jersey = match.group(3)
                if name:
                    profile['name'] = name
                if position:
                    profile['position'] = position
                if jersey:
                    profile['jersey'] = jersey
            # If jersey is in the second part after '|', prefer that
            if jersey_part:
                profile['jersey'] = jersey_part
        
        # Parse other profile information
        profile_text = profile_box.get_text()
        
        # Extract height
        height_match = re.search(r'Height:\s*([^()]+)\s*\((\d+)cm\)', profile_text)
        if height_match:
            profile['height_imperial'] = height_match.group(1).strip()
            profile['height_metric'] = height_match.group(2)
        
        # Extract weight
        weight_match = re.search(r'Weight:\s*([^()]+)\s*\((\d+)kg\)', profile_text)
        if weight_match:
            profile['weight_imperial'] = weight_match.group(1).strip()
            profile['weight_metric'] = weight_match.group(2)
        
        # Extract birth date and age
        birth_match = re.search(r'Born:\s*([^(]+)\s*\(([^)]+)\)', profile_text)
        if birth_match:
            profile['date_of_birth'] = birth_match.group(1).strip()
            profile['age'] = birth_match.group(2).strip()
        
        # Extract hometown
        hometown_match = re.search(r'Hometown:\s*([^\n]+)', profile_text)
        if hometown_match:
            profile['hometown'] = hometown_match.group(1).strip()
        
        # Extract nationality
        nationality_match = re.search(r'Nationality:\s*([^\n]+)', profile_text)
        if nationality_match:
            profile['nationality'] = nationality_match.group(1).strip()
        
        return profile
    
    def _parse_player_stats_table(self, html: str, league: str) -> pd.DataFrame:
        """
        Parse the player stats table from the Career/By_Split page
        
        Args:
            html: HTML content of the page
            league: League name for context
            
        Returns:
            pandas DataFrame containing parsed statistics
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the stats table - look for the specific league title
        table = None
        
        # Look for the table under the league-specific heading
        if league == "WNBA":
            # Look for "WNBA Regular Season Stats - Per Game"
            h2_tags = soup.find_all('h2')
            for h2 in h2_tags:
                if "WNBA Regular Season Stats - Per Game" in h2.get_text():
                    # Find the next table after this heading
                    next_elem = h2.find_next_sibling()
                    while next_elem and next_elem.name != 'table':
                        next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name == 'table':
                        table = next_elem
                        break
        else:
            # For other leagues, look for the pattern "{League} Season Stats - Per Game"
            h2_tags = soup.find_all('h2')
            for h2 in h2_tags:
                h2_text = h2.get_text()
                if f"{league} Season Stats - Per Game" in h2_text or f"{league} Regular Season Stats - Per Game" in h2_text:
                    # Find the next table after this heading
                    next_elem = h2.find_next_sibling()
                    while next_elem and next_elem.name != 'table':
                        next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name == 'table':
                        table = next_elem
                        break
        
        if not table:
            # Fallback: look for any table with the expected columns
            tables = soup.find_all('table')
            for t in tables:
                headers = [th.get_text(strip=True) for th in t.find_all('th')]
                if 'Season' in headers and 'Team' in headers and 'GP' in headers:
                    table = t
                    break
        
        if not table:
            # Return empty DataFrame if no table found
            return pd.DataFrame()
        
        # Parse the table
        rows = table.find_all('tr')
        if len(rows) < 2:  # Need at least header and one data row
            return pd.DataFrame()
        
        # Extract headers
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Clean up headers
        clean_headers = []
        for header in headers:
            # Remove any special characters and normalize
            clean_header = re.sub(r'[^\w\s]', '', header).strip()
            if clean_header:
                clean_headers.append(clean_header)
            else:
                clean_headers.append(header)
        
        # Extract data rows
        data_rows = []
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= len(clean_headers):
                row_data = []
                for cell in cells[:len(clean_headers)]:
                    # Get text and clean it
                    cell_text = cell.get_text(strip=True)
                    # Handle team links - extract team name
                    team_link = cell.find('a')
                    if team_link:
                        cell_text = team_link.get_text(strip=True)
                    row_data.append(cell_text)
                data_rows.append(row_data)
        
        # Create DataFrame
        if data_rows:
            df = pd.DataFrame(data_rows, columns=clean_headers)
            
            # Convert numeric columns
            numeric_columns = ['GP', 'GS', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 
                             'FTM', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
            
            for col in numeric_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except (ValueError, TypeError):
                        # Keep as string if conversion fails
                        pass
            
            return df
        else:
            return pd.DataFrame() 

    def _parse_league_players_table(self, html: str) -> pd.DataFrame:
        """
        Parse the league players table from the players listing page
        
        Args:
            html: HTML content of the page
            
        Returns:
            pandas DataFrame containing parsed player data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main players table
        table = soup.find('table')
        if not table:
            return pd.DataFrame()
        
        # Parse the table
        rows = table.find_all('tr')
        if len(rows) < 2:  # Need at least header and one data row
            return pd.DataFrame()
        
        # Extract headers
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Clean up headers
        clean_headers = []
        for header in headers:
            # Remove any special characters and normalize
            clean_header = re.sub(r'[^\w\s]', '', header).strip()
            if clean_header:
                clean_headers.append(clean_header)
            else:
                clean_headers.append(header)
        
        # Extract data rows
        data_rows = []
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= len(clean_headers):
                row_data = []
                for cell in cells[:len(clean_headers)]:
                    # Get text and clean it
                    cell_text = cell.get_text(strip=True)
                    # Handle player links - extract player name and ID
                    player_link = cell.find('a')
                    if player_link and 'Player' in clean_headers[1]:  # Assuming Player is the second column
                        cell_text = player_link.get_text(strip=True)
                        # Could extract player_id from href if needed
                        # player_id = player_link.get('href', '').split('/')[-1]
                    row_data.append(cell_text)
                data_rows.append(row_data)
        
        # Create DataFrame
        if data_rows:
            df = pd.DataFrame(data_rows, columns=clean_headers)
            
            # Convert numeric columns
            numeric_columns = ['#', 'Age', 'YOS']
            
            for col in numeric_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except (ValueError, TypeError):
                        # Keep as string if conversion fails
                        pass
            
            return df
        else:
            return pd.DataFrame() 