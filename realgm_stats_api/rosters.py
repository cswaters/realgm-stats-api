"""
Roster Scraper for RealGM Basketball Stats API
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin
from datetime import datetime


# Major leagues that use simple URL patterns
MAJOR_LEAGUES = {
    "nba": "NBA",
    "wnba": "WNBA"
}


def _is_major_league(league_name: str) -> bool:
    """Check if this is a major league that uses the simple URL pattern"""
    return league_name.lower() in MAJOR_LEAGUES


def _format_season_for_league(league_name: str, season: str) -> str:
    """
    Format season parameter based on league type
    
    Args:
        league_name: League name (nba, wnba, etc.)
        season: Season input (e.g., "2025" or "2024-2025")
        
    Returns:
        Formatted season string for URL
    """
    if league_name.lower() == "nba":
        # NBA: Convert "2024-2025" to "2025" or "2025" to "2025"
        if "-" in season:
            # Already in format "2024-2025", extract ending year
            return season.split("-")[1]
        else:
            # Single year like "2025", use as is
            return season
    elif league_name.lower() == "wnba":
        # WNBA: Always single year format
        if "-" in season:
            # Convert "2024-2025" to "2025"
            return season.split("-")[1]
        else:
            # Already single year like "2025"
            return season
    else:
        # International leagues: use as provided
        return season


class RosterScraper:
    """Scraper for RealGM roster data"""
    
    def __init__(self, session: requests.Session, base_url: str, rate_limit: float = 1.0):
        self.session = session
        self.base_url = base_url
        self.rate_limit = rate_limit
    
    def get_team_roster(self, 
                       league_id: int = None,
                       league_name: str = None,
                       team_id: int = None,
                       team_name: str = None,
                       season: str = "2025") -> Dict:
        """
        Get roster for a specific team
        
        Args:
            league_id: League ID (not required for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            team_id: Team ID
            team_name: Team name slug
            season: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)
            
        Returns:
            Dictionary containing roster data:
            {
                'league_id': int,
                'league_name': str,
                'team_id': int,
                'team_name': str,
                'season': str,
                'scraped_at': str,
                'roster': List[Dict],
                'metadata': Dict
            }
        """
        # Build the URL based on league type
        if _is_major_league(league_name):
            # NBA/WNBA use: /nba/teams/Boston-Celtics/2/Rosters/Regular/2025
            formatted_season = _format_season_for_league(league_name, season)
            url_path = f"/{league_name.lower()}/teams/{team_name}/{team_id}/Rosters/Regular/{formatted_season}"
        else:
            # International leagues use the existing pattern
            url_path = f"/international/league/{league_id}/{league_name}/team/{team_id}/{team_name}/rosters/{season}"
        
        url = urljoin(self.base_url, url_path)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.rate_limit)
            
            return self._parse_roster_page(response.text, league_id, league_name, team_id, team_name, season)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching roster: {e}")
    
    def get_teams_from_teams_page(self, league_id: int, league_name: str) -> List[Dict]:
        """
        Get list of teams from the league teams page
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of team dictionaries with id, name, and name_slug
        """
        if _is_major_league(league_name):
            url_path = f"/{league_name.lower()}/teams"
        else:
            url_path = f"/international/league/{league_id}/{league_name}/teams"
        
        url = urljoin(self.base_url, url_path)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            teams = []
            
            if _is_major_league(league_name):
                # Major leagues have a different structure - teams are in navigation menus
                # Look for team links in the navigation structure
                team_links = soup.find_all('a', href=re.compile(r'/teams/[^/]+/\d+'))
                for link in team_links:
                    href = link.get('href', '')
                    team_name = link.get_text(strip=True)
                    
                    # Extract team ID from URL: /nba/teams/Boston-Celtics/2
                    team_id_match = re.search(r'/teams/[^/]+/(\d+)', href)
                    if team_id_match:
                        team_id = team_id_match.group(1)
                        team_name_slug = self._create_team_slug(team_name)
                        
                        teams.append({
                            'id': team_id,
                            'name': team_name,
                            'name_slug': team_name_slug,
                            'url': href
                        })
            else:
                # International leagues use the existing pattern
                # Find the teams table
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        # Find team link in the first column
                        team_cell = row.find('td')
                        if team_cell:
                            team_link = team_cell.find('a')
                            if team_link:
                                team_name = team_link.get_text(strip=True)
                                team_url = team_link.get('href', '')
                                
                                # Extract team ID from URL
                                # For major leagues: /nba/teams/Boston-Celtics/2
                                # For international: /international/league/15/German-BBL/team/142/ALBA-Berlin
                                if _is_major_league(league_name):
                                    team_id_match = re.search(r'/teams/[^/]+/(\d+)', team_url)
                                else:
                                    team_id_match = re.search(r'/team/(\d+)/', team_url)
                                
                                if team_id_match:
                                    team_id = team_id_match.group(1)
                                    team_name_slug = self._create_team_slug(team_name)
                                    
                                    teams.append({
                                        'id': team_id,
                                        'name': team_name,
                                        'name_slug': team_name_slug,
                                        'url': team_url
                                    })
            
            return teams
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching teams from teams page: {e}")
    
    def get_league_rosters(self,
                          league_id: int,
                          league_name: str,
                          season: str = "2025",
                          output_file: Optional[str] = None) -> Dict:
        """
        Get rosters for all teams in a league and optionally save to file
        
        Args:
            league_id: League ID
            league_name: League name slug
            season: Season year
            output_file: Optional output file path for JSON export
            
        Returns:
            Dictionary containing league info and all team rosters
        """
        # Get teams from the teams page
        print(f"Fetching teams for {league_name}...")
        teams = self.get_teams_from_teams_page(league_id, league_name)
        
        if not teams:
            raise Exception(f"No teams found for league {league_name}")
        
        print(f"Found {len(teams)} teams. Fetching rosters...")
        
        # Initialize result structure
        league_rosters = {
            'league_id': league_id,
            'league_name': league_name,
            'season': season,
            'scraped_at': datetime.now().isoformat(),
            'total_teams': len(teams),
            'teams': {}
        }
        
        # Fetch roster for each team
        for i, team in enumerate(teams, 1):
            try:
                print(f"  [{i}/{len(teams)}] Fetching roster for {team['name']}...")
                
                team_roster = self.get_team_roster(
                    league_id=league_id,
                    league_name=league_name,
                    team_id=team['id'],
                    team_name=team['name_slug'],
                    season=season
                )
                
                league_rosters['teams'][team['name']] = team_roster
                
                # Add delay between requests
                time.sleep(self.rate_limit)
                
            except Exception as e:
                print(f"    Error fetching roster for {team['name']}: {e}")
                # Add empty entry to maintain structure
                league_rosters['teams'][team['name']] = {
                    'error': str(e),
                    'league_id': league_id,
                    'league_name': league_name,
                    'team_id': team['id'],
                    'team_name': team['name_slug'],
                    'season': season,
                    'scraped_at': datetime.now().isoformat()
                }
                continue
        
        # Save to file if specified
        if output_file:
            try:
                import json
                with open(output_file, 'w') as f:
                    json.dump(league_rosters, f, indent=2)
                print(f"\nLeague rosters saved to {output_file}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        
        return league_rosters
    
    def _create_team_slug(self, team_name: str) -> str:
        """
        Create a URL-friendly slug from team name
        
        Args:
            team_name: Team name
            
        Returns:
            URL-friendly slug
        """
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', team_name)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.lower()
    
    def _parse_roster_page(self, html: str, league_id: int, league_name: str, team_id: int, team_name: str, season: str) -> Dict:
        """
        Parse the roster HTML page for NBA, WNBA, or international leagues.
        Returns a dictionary with all available fields for each player, using None for missing data.
        Output structure:
        - NBA: Jersey, Player, Pos, HT, WT, YOS, Pre-Draft Team, Draft Status, Nationality, Free Agent Info
        - WNBA: Jersey, Player, Pos, HT, WT, YOS, Pre-Draft Team, Draft Status, Nationality
        - International: #, Player, Pos, Height, Weight, Age, Birth City, NBA Draft Status, Nationality
        """
        soup = BeautifulSoup(html, 'html.parser')
        roster_data = {
            'league_id': league_id,
            'league_name': league_name,
            'team_id': team_id,
            'team_name': team_name,
            'season': season,
            'scraped_at': datetime.now().isoformat(),
            'roster': [],
            'metadata': {}
        }
        # Find the main roster table
        table = soup.find('table')
        if not table:
            return roster_data
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        # Map headers to normalized keys
        header_map = {}
        for i, h in enumerate(headers):
            h_norm = h.lower().replace(' ', '_').replace('#', 'number').replace('jersey', 'number')
            if h_norm in ['number', 'jersey', '#']:
                header_map[i] = 'number'
            elif h_norm == 'player':
                header_map[i] = 'name'
            elif h_norm == 'pos':
                header_map[i] = 'position'
            elif h_norm in ['ht', 'height']:
                header_map[i] = 'height'
            elif h_norm in ['wt', 'weight']:
                header_map[i] = 'weight'
            elif h_norm == 'yos':
                header_map[i] = 'years_of_service'
            elif h_norm == 'pre-draft_team':
                header_map[i] = 'pre_draft_team'
            elif h_norm == 'draft_status':
                header_map[i] = 'draft_status'
            elif h_norm == 'nationality':
                header_map[i] = 'nationality'
            elif h_norm == 'free_agent_info':
                header_map[i] = 'free_agent_info'
            elif h_norm == 'age':
                header_map[i] = 'age'
            elif h_norm == 'birth_city':
                header_map[i] = 'birth_city'
            elif h_norm == 'nba_draft_status':
                header_map[i] = 'nba_draft_status'
            else:
                header_map[i] = h_norm
        # Extract data rows
        for row in table.find_all('tr')[1:]:
            cells = row.find_all(['td', 'th'])
            if not cells or len(cells) < 2:
                continue
            player = {}
            for i, cell in enumerate(cells):
                key = header_map.get(i)
                value = cell.get_text(strip=True)
                if key == 'name':
                    link = cell.find('a')
                    if link:
                        player['name'] = link.get_text(strip=True)
                        player['player_id'] = link.get('href', '').split('/')[-1]
                    else:
                        player['name'] = value
                elif key:
                    player[key] = value if value and value != '-' else None
            # Fill in missing fields with None
            for field in ['number', 'name', 'player_id', 'position', 'height', 'weight', 'years_of_service', 'pre_draft_team', 'draft_status', 'nationality', 'free_agent_info', 'age', 'birth_city', 'nba_draft_status']:
                if field not in player:
                    player[field] = None
            roster_data['roster'].append(player)
        return roster_data
    
    def _parse_roster_table(self, table) -> List[Dict]:
        """
        Parse the roster table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            List of player dictionaries
        """
        players = []
        
        # Find the table body
        tbody = table.find('tbody')
        if not tbody:
            return players
        
        # Get headers from thead
        thead = table.find('thead')
        headers = []
        if thead:
            header_row = thead.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # Parse each player row
        for row in tbody.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                player = self._parse_player_row(cells, headers)
                if player:
                    players.append(player)
        
        return players
    
    def _parse_player_row(self, cells, headers) -> Optional[Dict]:
        """
        Parse a player row in the roster table
        
        Args:
            cells: List of table cells
            headers: List of column headers
            
        Returns:
            Dictionary containing player information or None if invalid
        """
        player = {}
        
        for i, header in enumerate(headers):
            if i >= len(cells):
                continue
            
            cell = cells[i]
            value = cell.get_text(strip=True)
            
            if header == '#':
                player['number'] = value if value and value != '-' else None
            elif header == 'Player':
                link = cell.find('a')
                if link:
                    player['name'] = link.get_text(strip=True)
                    player['player_id'] = link.get('href', '').split('/')[-1]
                    player['player_url'] = urljoin(self.base_url, link.get('href', ''))
                else:
                    player['name'] = value
            elif header == 'Pos':
                player['position'] = value
            elif header == 'Height':
                player['height'] = value
            elif header == 'Weight':
                player['weight'] = value
            elif header == 'Age':
                try:
                    player['age'] = int(value) if value and value != '-' else None
                except ValueError:
                    player['age'] = None
            elif header == 'Birth City':
                player['birth_city'] = value if value and value != '-' else None
            elif header == 'NBA Draft Status':
                player['nba_draft_status'] = value if value and value != '-' else None
            elif header == 'Nationality':
                player['nationality'] = value if value and value != '-' else None
            else:
                # Handle any other columns
                if value and value != '-':
                    player[header.lower().replace(' ', '_')] = value
        
        # Only return player if we have at least a name
        return player if player.get('name') else None
    
    def _extract_page_metadata(self, soup) -> Dict:
        """
        Extract metadata from the page
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {}
        
        # Extract page title
        title = soup.find('title')
        if title:
            metadata['page_title'] = title.get_text(strip=True)
        
        # Extract breadcrumb navigation
        breadcrumbs = soup.find('nav', class_='breadcrumb')
        if breadcrumbs:
            breadcrumb_items = breadcrumbs.find_all('a')
            metadata['breadcrumbs'] = [item.get_text(strip=True) for item in breadcrumb_items]
        
        # Extract season information if available
        season_select = soup.find('select', {'name': 'season'})
        if season_select:
            selected_option = season_select.find('option', selected=True)
            if selected_option:
                metadata['current_season'] = selected_option.get_text(strip=True)
        
        return metadata 