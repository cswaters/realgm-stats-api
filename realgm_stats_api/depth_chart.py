"""
Depth Chart Scraper for RealGM Basketball Stats API
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


class DepthChartScraper:
    """Scraper for RealGM depth chart data"""
    
    def __init__(self, session: requests.Session, base_url: str, rate_limit: float = 1.0):
        self.session = session
        self.base_url = base_url
        self.rate_limit = rate_limit
    
    def get_depth_chart(self, 
                       league_id: int = None,
                       league_name: str = None,
                       team_id: int = None,
                       team_name: str = None,
                       season: str = "2025") -> Dict:
        """
        Get depth chart for a specific team
        
        Args:
            league_id: League ID (not required for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            team_id: Team ID
            team_name: Team name slug
            season: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)
            
        Returns:
            Dictionary containing depth chart data
        """
        # Build the URL based on league type
        if _is_major_league(league_name):
            if league_name.lower() == "wnba":
                raise Exception("WNBA does not have depth charts available")
            url_path = f"/{league_name.lower()}/teams/{team_name}/{team_id}/depth-charts"
        else:
            url_path = f"/international/league/{league_id}/{league_name}/team/{team_id}/{team_name}/depth-charts/{season}"
        
        url = urljoin(self.base_url, url_path)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Add delay to be respectful to the server
            time.sleep(self.rate_limit)
            
            return self._parse_depth_chart_page(response.text, league_id, league_name, team_id, team_name, season)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching depth chart: {e}")
    
    def get_team_depth_charts(self,
                             league_id: int,
                             league_name: str,
                             season: str = "2025") -> Dict[str, Dict]:
        """
        Get depth charts for all teams in a league
        
        Args:
            league_id: League ID
            league_name: League name slug
            season: Season year
            
        Returns:
            Dictionary mapping team names to their depth charts
        """
        # First get the list of teams
        teams = self._get_teams_in_league(league_id, league_name, season)
        
        depth_charts = {}
        for team in teams:
            try:
                team_depth_chart = self.get_depth_chart(
                    league_id=league_id,
                    league_name=league_name,
                    team_id=team['id'],
                    team_name=team['name_slug'],
                    season=season
                )
                depth_charts[team['name']] = team_depth_chart
                
                # Add delay between requests
                time.sleep(self.rate_limit)
                
            except Exception as e:
                print(f"Error fetching depth chart for {team['name']}: {e}")
                continue
        
        return depth_charts
    
    def _get_teams_in_league(self, league_id: int, league_name: str, season: str) -> List[Dict]:
        """
        Get list of teams in a league
        
        Args:
            league_id: League ID
            league_name: League name slug
            season: Season year
            
        Returns:
            List of team dictionaries
        """
        url_path = f"/international/league/{league_id}/{league_name}/stats/{season}/Averages/Qualified/All/points/All/desc/1/Regular_Season"
        url = urljoin(self.base_url, url_path)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            teams = []
            
            # Find team filter dropdown
            team_select = soup.find('select', {'name': 'team'})
            if team_select:
                for option in team_select.find_all('option'):
                    if option.get('value') and option.get('value') != 'All':
                        team_name = option.text.strip()
                        team_id = option.get('value')
                        team_name_slug = self._create_team_slug(team_name)
                        teams.append({
                            'id': team_id,
                            'name': team_name,
                            'name_slug': team_name_slug
                        })
            
            return teams
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching teams: {e}")
    
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
    
    def _parse_depth_chart_page(self, html: str, league_id: int, league_name: str, 
                               team_id: int, team_name: str, season: str) -> Dict:
        """
        Parse the depth chart HTML page
        
        Args:
            html: HTML content of the page
            league_id: League ID
            league_name: League name slug
            team_id: Team ID
            team_name: Team name slug
            season: Season year
            
        Returns:
            Dictionary containing parsed depth chart data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        depth_chart_data = {
            'league_id': league_id,
            'league_name': league_name,
            'team_id': team_id,
            'team_name': team_name,
            'season': season,
            'scraped_at': datetime.now().isoformat(),
            'depth_chart': {},
            'team_leaders': {},
            'metadata': {}
        }
        
        # Find the main depth chart table
        depth_chart_table = soup.find('table')
        if depth_chart_table:
            depth_chart_data['depth_chart'] = self._parse_depth_chart_table(depth_chart_table)
        
        # Find team leaders section
        leaders_section = soup.find('h3', string=re.compile(r'.*Leaders'))
        if leaders_section:
            leaders_table = leaders_section.find_next('table')
            if leaders_table:
                depth_chart_data['team_leaders'] = self._parse_team_leaders_table(leaders_table)
        
        # Extract metadata
        depth_chart_data['metadata'] = self._extract_page_metadata(soup)
        
        return depth_chart_data
    
    def _parse_depth_chart_table(self, table) -> Dict:
        """
        Parse the depth chart table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            Dictionary containing depth chart structure
        """
        depth_chart = {}
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            
            # Get role (Starters, Rotation, Lim PT, etc.)
            role_cell = cells[0]
            role_text = role_cell.get_text(strip=True)
            
            # Extract role from strong tag if present
            strong = role_cell.find('strong')
            if strong:
                role = strong.get_text(strip=True)
            else:
                role = role_text
            
            # Clean up role name
            if role in ['Starters', 'Rotation', 'Lim PT']:
                role_key = role.lower().replace(' ', '_')
                depth_chart[role_key] = {}
                
                # Parse each position column
                for i, pos in enumerate(positions):
                    if i + 1 < len(cells):
                        cell = cells[i + 1]
                        player_data = self._parse_player_cell(cell)
                        if player_data:
                            depth_chart[role_key][pos] = player_data
        
        return depth_chart
    
    def _parse_player_cell(self, cell) -> Optional[Dict]:
        """
        Parse a player cell in the depth chart
        
        Args:
            cell: BeautifulSoup cell element
            
        Returns:
            Dictionary containing player information or None if empty
        """
        link = cell.find('a')
        if not link:
            return None
        
        # Get player name and ID
        player_name = link.get_text(strip=True)
        player_url = link.get('href', '')
        player_id = player_url.split('/')[-1] if player_url else None
        
        # Get full cell text to extract stats
        cell_text = cell.get_text('\n', strip=True)
        lines = cell_text.split('\n')
        
        player_data = {
            'name': player_name,
            'player_id': player_id,
            'player_url': urljoin(self.base_url, player_url) if player_url else None
        }
        
        # Extract season stats if present
        if len(lines) > 1:
            stats_line = lines[1].strip()
            if stats_line and not stats_line.startswith(player_name):
                player_data['season_stats'] = self._parse_season_stats(stats_line)
        
        return player_data
    
    def _parse_season_stats(self, stats_line: str) -> Dict:
        """
        Parse season stats from a stats line
        
        Args:
            stats_line: String containing stats (e.g., "17.4p 3.8r 2.8a")
            
        Returns:
            Dictionary containing parsed stats
        """
        stats = {}
        
        # Parse points
        points_match = re.search(r'(\d+\.?\d*)p', stats_line)
        if points_match:
            stats['points'] = float(points_match.group(1))
        
        # Parse rebounds
        rebounds_match = re.search(r'(\d+\.?\d*)r', stats_line)
        if rebounds_match:
            stats['rebounds'] = float(rebounds_match.group(1))
        
        # Parse assists
        assists_match = re.search(r'(\d+\.?\d*)a', stats_line)
        if assists_match:
            stats['assists'] = float(assists_match.group(1))
        
        # Parse steals
        steals_match = re.search(r'(\d+\.?\d*)s', stats_line)
        if steals_match:
            stats['steals'] = float(steals_match.group(1))
        
        # Parse blocks
        blocks_match = re.search(r'(\d+\.?\d*)b', stats_line)
        if blocks_match:
            stats['blocks'] = float(blocks_match.group(1))
        
        return stats
    
    def _parse_team_leaders_table(self, table) -> Dict:
        """
        Parse team leaders table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            Dictionary containing team leaders
        """
        leaders = {}
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                stat_name = cells[0].get_text(strip=True)
                player_cell = cells[1]
                
                link = player_cell.find('a')
                if link:
                    player_name = link.get_text(strip=True)
                    player_url = link.get('href', '')
                    player_id = player_url.split('/')[-1] if player_url else None
                    
                    # Get the stat value
                    stat_value = cells[2].get_text(strip=True) if len(cells) > 2 else None
                    
                    leaders[stat_name] = {
                        'player_name': player_name,
                        'player_id': player_id,
                        'player_url': urljoin(self.base_url, player_url) if player_url else None,
                        'value': stat_value
                    }
        
        return leaders
    
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
        
        return metadata
    
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
    
    def get_league_depth_charts(self,
                               league_id: int,
                               league_name: str,
                               season: str = "2025",
                               output_file: Optional[str] = None) -> Dict:
        """
        Get depth charts for all teams in a league and optionally save to file
        
        Args:
            league_id: League ID
            league_name: League name slug
            season: Season year
            output_file: Optional output file path for JSON export
            
        Returns:
            Dictionary containing league info and all team depth charts
        """
        # Get teams from the teams page
        print(f"Fetching teams for {league_name}...")
        teams = self.get_teams_from_teams_page(league_id, league_name)
        
        if not teams:
            raise Exception(f"No teams found for league {league_name}")
        
        print(f"Found {len(teams)} teams. Fetching depth charts...")
        
        # Initialize result structure
        league_depth_charts = {
            'league_id': league_id,
            'league_name': league_name,
            'season': season,
            'scraped_at': datetime.now().isoformat(),
            'total_teams': len(teams),
            'teams': {}
        }
        
        # Fetch depth chart for each team
        for i, team in enumerate(teams, 1):
            try:
                print(f"  [{i}/{len(teams)}] Fetching depth chart for {team['name']}...")
                
                team_depth_chart = self.get_depth_chart(
                    league_id=league_id,
                    league_name=league_name,
                    team_id=team['id'],
                    team_name=team['name_slug'],
                    season=season
                )
                
                league_depth_charts['teams'][team['name']] = team_depth_chart
                
                # Add delay between requests
                time.sleep(self.rate_limit)
                
            except Exception as e:
                print(f"    Error fetching depth chart for {team['name']}: {e}")
                # Add empty entry to maintain structure
                league_depth_charts['teams'][team['name']] = {
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
                    json.dump(league_depth_charts, f, indent=2)
                print(f"\nLeague depth charts saved to {output_file}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        
        return league_depth_charts 