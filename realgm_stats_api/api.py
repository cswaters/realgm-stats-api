"""
RealGM Basketball Stats API
A Python package to scrape and filter RealGM basketball statistics
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
import pandas as pd
from urllib.parse import urljoin
import re
import time
from .boxscore import BoxscoreScraper
from .depth_chart import DepthChartScraper
from .rosters import RosterScraper
from .player import PlayerScraper


class RealGMStatsAPI:
    """
    A class to interact with RealGM basketball statistics
    """
    
    def __init__(self, base_url: str = "https://basketball.realgm.com"):
        self.base_url = base_url
        self.session = requests.Session()
        # Set headers to mimic browser behavior
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.boxscore_scraper = BoxscoreScraper(self.session, self.base_url)
        self.depth_chart_scraper = DepthChartScraper(self.session, self.base_url)
        self.roster_scraper = RosterScraper(self.session, self.base_url)
        self.player_scraper = PlayerScraper(self.session, self.base_url)
    
    def get_league_stats(self, 
                        league_id: int = 31,
                        league_name: str = "Romanian-Divizia-A",
                        season: str = "2025",
                        stat_type: Union[str, List[str]] = "Averages",
                        qualified: bool = True,
                        prospects: str = "All",
                        team: str = "All",
                        position: str = "All",
                        sort_column: str = "points",
                        sort_order: str = "desc",
                        page: int = 1,
                        season_type: str = "Regular_Season") -> pd.DataFrame:
        """
        Get basketball statistics for a specific league and filters
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            season: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)
            stat_type: Type of stats or list of stat types. Options:
                - "Averages"
                - "Totals"
                - "Per_48"
                - "Per_40"
                - "Per_36"
                - "Per_Minute"
                - "Minute_Per"
                - "Misc_Stats"
                - "Advanced_Stats"
            qualified: Whether to show only qualified players
            prospects: Prospect filter ("All", "Pro", "Draft")
            team: Team filter ("All" or specific team)
            position: Position filter ("All", "PG", "SG", "SF", "PF", "C")
            sort_column: Column to sort by
            sort_order: Sort order ("desc" or "asc")
            page: Page number
            season_type: Season type ("Regular_Season")
        
        Returns:
            pandas DataFrame containing the statistics. If multiple stat types are requested,
            the DataFrames are merged on player name and team.
        """
        # Convert single stat_type to list for consistent handling
        stat_types = [stat_type] if isinstance(stat_type, str) else stat_type
        
        # Validate stat types
        invalid_types = [st for st in stat_types if st not in STAT_TYPES]
        if invalid_types:
            raise ValueError(f"Invalid stat type(s): {invalid_types}. Valid types are: {STAT_TYPES}")
        
        # Get stats for each type
        dfs = []
        for st in stat_types:
            # Build the URL using the new helper method
            url = self._build_stats_url(
                league_id=league_id,
                league_name=league_name,
                season=season,
                stat_type=st,
                qualified=qualified,
                prospects=prospects,
                team=team,
                sort_column=sort_column,
                position=position,
                sort_order=sort_order,
                page=page,
                season_type=season_type
            )
            
            # Add position as query parameter if not "All"
            params = {}
            if position != "All":
                params[position.lower()] = ""
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                # Add delay to be respectful to the server
                time.sleep(1)
                
                df = self._parse_stats_table(response.text)
                dfs.append(df)
                
            except requests.RequestException as e:
                raise Exception(f"Error fetching data for stat type {st}: {e}")
        
        # If only one stat type, return its DataFrame
        if len(dfs) == 1:
            return dfs[0]
        
        # Merge DataFrames on player name and team
        result = dfs[0]
        for df in dfs[1:]:
            result = pd.merge(result, df, on=['Player', 'Team'], how='left')
        
        return result

    def _build_stats_url(self, league_id: int, league_name: str, season: str, stat_type: str, 
                         qualified: bool, prospects: str, team: str, sort_column: str, 
                         position: str, sort_order: str, page: int, season_type: str) -> str:
        """Build the appropriate URL based on league type"""
        
        if _is_major_league(league_name):
            # Major leagues use simple URL pattern
            if team != "All":
                # For WNBA team stats, use the correct URL pattern with team ID
                if league_name.lower() == "wnba":
                    # WNBA team stats: /wnba/teams/Golden-State-Valkyries/7/Stats
                    # We need to map team names to their IDs
                    wnba_team_ids = {
                        "Atlanta Dream": 1,
                        "Chicago Sky": 3,
                        "Connecticut Sun": 5,
                        "Dallas Wings": 6,
                        "Golden State Valkyries": 7,
                        "Indiana Fever": 9,
                        "Los Angeles Sparks": 10,
                        "Las Vegas Aces": 11,
                        "Seattle Storm": 18,
                        "Washington Mystics": 19,
                        "Minnesota Lynx": 13,
                        "New York Liberty": 14,
                        "Phoenix Mercury": 15
                    }
                    team_id = wnba_team_ids.get(team, 1)
                    url_path = f"/{league_name.lower()}/teams/{team.replace(' ', '-')}/{team_id}/Stats"
                else:
                    # NBA team stats: /nba/team/Boston-Celtics/stats/2025/Averages
                    formatted_season = _format_season_for_league(league_name, season)
                    url_path = f"/{league_name.lower()}/team/{team}/stats/{formatted_season}/{stat_type}"
            else:
                # League-wide stats
                formatted_season = _format_season_for_league(league_name, season)
                url_path = f"/{league_name.lower()}/stats/{formatted_season}/{stat_type}"
        else:
            # International leagues use the complex pattern
            qualified_str = "Qualified" if qualified else "All"
            if team != "All":
                url_path = f"/international/league/{league_id}/{league_name}/team/{team}/stats/{season}/{stat_type}/{qualified_str}/{prospects}"
            else:
                url_path = f"/international/league/{league_id}/{league_name}/stats/{season}/{stat_type}/{qualified_str}/{prospects}/{sort_column}/{position}/{sort_order}/{page}/{season_type}"
        
        return urljoin(self.base_url, url_path)
    
    def _parse_stats_table(self, html: str) -> pd.DataFrame:
        """
        Parse the HTML table containing player statistics
        
        Args:
            html: HTML content of the page
            
        Returns:
            pandas DataFrame with parsed statistics
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main stats table
        table = soup.find('table', {'data-toggle': 'table'})
        
        if not table:
            raise Exception("Could not find stats table in the response")
        
        # Extract headers
        headers = []
        header_row = table.find('thead').find('tr')
        for th in header_row.find_all('th'):
            headers.append(th.get_text(strip=True))
        
        # Extract data rows
        data = []
        tbody = table.find('tbody')
        for row in tbody.find_all('tr'):
            row_data = []
            cells = row.find_all('td')
            
            for i, cell in enumerate(cells):
                if i == 1:  # Player name column - extract just the name
                    link = cell.find('a')
                    if link:
                        row_data.append(link.get_text(strip=True))
                    else:
                        row_data.append(cell.get_text(strip=True))
                elif i == 2:  # Team column - extract team abbreviation
                    link = cell.find('a')
                    if link:
                        row_data.append(link.get_text(strip=True))
                    else:
                        row_data.append(cell.get_text(strip=True))
                else:
                    text = cell.get_text(strip=True)
                    # Try to convert numeric values
                    if text and text not in ['', '-']:
                        try:
                            # Handle percentages
                            if text.startswith('.'):
                                row_data.append(float(text))
                            # Handle regular numbers
                            elif text.replace('.', '').replace('-', '').isdigit():
                                if '.' in text:
                                    row_data.append(float(text))
                                else:
                                    row_data.append(int(text))
                            else:
                                row_data.append(text)
                        except ValueError:
                            row_data.append(text)
                    else:
                        row_data.append(None)
            
            if row_data:  # Only add non-empty rows
                data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df
    
    def get_available_filters(self, 
                             league_id: int = 31,
                             league_name: str = "Romanian-Divizia-A") -> Dict[str, List[str]]:
        """
        Extract available filter options from the stats page
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            Dictionary containing available filter options
        """
        if _is_major_league(league_name):
            url_path = f"/{league_name.lower()}/stats"
        else:
            url_path = f"/international/league/{league_id}/{league_name}/stats"
        
        url = urljoin(self.base_url, url_path)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            filters = {}
            
            # Find all select elements in the page navigation
            nav_container = soup.find('div', class_='page-navigation')
            if nav_container:
                for select in nav_container.find_all('select'):
                    # Get the label
                    label_elem = select.find_previous('label')
                    if label_elem:
                        label = label_elem.get_text(strip=True).replace(':', '')
                        options = []
                        for option in select.find_all('option'):
                            options.append({
                                'value': option.get('value', ''),
                                'text': option.get_text(strip=True)
                            })
                        filters[label] = options
            
            return filters
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching filter options: {e}")
    
    def get_team_list(self, 
                     league_id: int = 31,
                     league_name: str = "Romanian-Divizia-A",
                     season: str = "2025") -> List[Dict[str, str]]:
        """
        Get list of teams in the league
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            season: Season year (e.g., "2025" for WNBA, "2024-2025" or "2025" for NBA)
            
        Returns:
            List of team dictionaries with name and ID
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
                        teams.append({
                            'id': team_id,
                            'name': team_name
                        })
            else:
                # International leagues use the existing pattern
                # Find the teams table
                table = soup.find('table', {'data-toggle': 'table'})
                if table:
                    tbody = table.find('tbody')
                    for row in tbody.find_all('tr'):
                        team_cell = row.find('td')
                        if team_cell:
                            link = team_cell.find('a')
                            if link:
                                team_name = link.get_text(strip=True)
                                team_url = link.get('href', '')
                                # Extract team ID from URL
                                team_id_match = re.search(r'/team/(\d+)/', team_url)
                                team_id = team_id_match.group(1) if team_id_match else ""
                                
                                teams.append({
                                    'id': team_id,
                                    'name': team_name,
                                    'url': team_url
                                })
            
            return teams
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching team list: {e}")

    def get_game_dates(self, league_id: int, league_name: str = None) -> List[str]:
        """
        Get available game dates for a league
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of dates in YYYY-MM-DD format
        """
        return self.boxscore_scraper.get_game_dates(league_id, league_name)

    def get_boxscore_links(self, league_id: int, date: str, league_name: str = None) -> List[Dict[str, str]]:
        """
        Get boxscore links for games on a specific date
        
        Args:
            league_id: League ID (not used for major leagues)
            date: Date in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of dictionaries containing game information:
            {
                'url': str,
                'game_id': str,
                'date': str,
                'away_team': str,
                'home_team': str,
                'matchup': str
            }
        """
        return self.boxscore_scraper.get_boxscore_links(league_id, date, league_name)

    def get_upcoming_games(self, league_id: int, date: str, league_name: str = None) -> List[Dict[str, str]]:
        """
        Get upcoming games for a specific date
        
        Args:
            league_id: League ID (not used for major leagues)
            date: Date in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of dictionaries containing upcoming game information:
            {
                'date': str,
                'time': str,
                'home': str,
                'away': str,
                'location': str,
                'type': str
            }
        """
        return self.boxscore_scraper.get_upcoming_games(league_id, date, league_name)

    def get_boxscore(self, game_info: Dict[str, str]) -> Dict:
        """
        Get detailed boxscore data for a game
        
        Args:
            game_info: Dictionary containing game information from get_boxscore_links()
            
        Returns:
            Dictionary containing detailed boxscore data:
            {
                'game_id': str,
                'date': str,
                'url': str,
                'away_team': str,
                'home_team': str,
                'scraped_at': str,
                'scores': Dict,
                'advanced_stats': Dict,
                'four_factors': Dict,
                'player_stats': Dict,
                'depth_charts': Dict,
                'metadata': Dict
            }
        """
        return self.boxscore_scraper.parse_boxscore(game_info)

    def get_boxscore_by_id(self, game_id: str, league_id: int, date: str, league_name: str = None) -> Dict:
        """
        Get boxscore data for a specific game ID
        
        Args:
            game_id: Game ID
            league_id: League ID (not used for major leagues)
            date: Date in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            Dictionary containing detailed boxscore data
        """
        links = self.get_boxscore_links(league_id, date, league_name)
        for game in links:
            if game['game_id'] == game_id:
                return self.get_boxscore(game)
        raise ValueError(f"Game ID {game_id} not found for date {date}")

    def get_boxscores_for_date(self, league_id: int, date: str, league_name: str = None) -> List[Dict]:
        """
        Get boxscore data for all games on a specific date
        
        Args:
            league_id: League ID (not used for major leagues)
            date: Date in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of dictionaries containing detailed boxscore data for each game
        """
        links = self.get_boxscore_links(league_id, date, league_name)
        return [self.get_boxscore(game) for game in links]

    def get_boxscores_for_date_range(self, league_id: int, start_date: str, end_date: str, league_name: str = None) -> List[Dict]:
        """
        Get boxscore data for all games in a date range
        
        Args:
            league_id: League ID (not used for major leagues)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of dictionaries containing detailed boxscore data for each game
        """
        all_dates = self.get_game_dates(league_id, league_name)
        start = all_dates.index(start_date) if start_date in all_dates else 0
        end = all_dates.index(end_date) + 1 if end_date in all_dates else len(all_dates)
        date_range = all_dates[start:end]
        
        all_boxscores = []
        for date in date_range:
            boxscores = self.get_boxscores_for_date(league_id, date, league_name)
            all_boxscores.extend(boxscores)
            time.sleep(self.boxscore_scraper.rate_limit)  # Respect rate limit
            
        return all_boxscores

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
        return self.depth_chart_scraper.get_depth_chart(
            league_id=league_id,
            league_name=league_name,
            team_id=team_id,
            team_name=team_name,
            season=season
        )
    
    def get_team_depth_charts(self,
                             league_id: int,
                             league_name: str,
                             season: str = "2025") -> Dict[str, Dict]:
        """
        Get depth charts for all teams in a league
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            season: Season year
            
        Returns:
            Dictionary mapping team names to their depth charts
        """
        return self.depth_chart_scraper.get_team_depth_charts(
            league_id=league_id,
            league_name=league_name,
            season=season
        )
    
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

    def scrape_league_teams(self, league_name: str) -> Dict[str, Dict]:
        """
        Scrape team information from a league's teams page and return a mapping
        of team names to their IDs and slugs.
        
        Args:
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            Dictionary mapping team names to their info:
            {
                "Team Name": {
                    "id": "team_id",
                    "slug": "team-slug",
                    "url": "team_url"
                }
            }
        """
        try:
            teams = self.get_teams_from_teams_page(league_id=None, league_name=league_name)
            
            # Create a mapping of team names to their info
            team_mapping = {}
            for team in teams:
                team_mapping[team['name']] = {
                    'id': team['id'],
                    'slug': team['name_slug'],
                    'url': team['url']
                }
            
            return team_mapping
            
        except Exception as e:
            raise Exception(f"Error scraping teams for {league_name}: {e}")

    def print_league_teams(self, league_name: str):
        """
        Print all teams for a league in a formatted way.
        
        Args:
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
        """
        try:
            teams = self.get_teams_from_teams_page(league_id=None, league_name=league_name)
            
            print(f'{league_name.upper()} Teams:')
            print('=' * 50)
            
            for team in teams:
                print(f"Name: {team['name']}")
                print(f"Slug: {team['name_slug']}")
                print(f"ID: {team['id']}")
                print(f"URL: {team['url']}")
                print('-' * 30)
                
        except Exception as e:
            print(f"Error: {e}")

    def get_team_mapping_for_code(self, league_name: str) -> str:
        """
        Generate Python code for team ID mapping that can be used in the API.
        
        Args:
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            String containing Python code for the team mapping
        """
        try:
            team_mapping = self.scrape_league_teams(league_name)
            
            code_lines = [f'# {league_name.upper()} team mapping']
            code_lines.append(f'{league_name.lower()}_team_ids = {{')
            
            for team_name, info in team_mapping.items():
                code_lines.append(f'    "{team_name}": {info["id"]},')
            
            code_lines.append('}')
            
            return '\n'.join(code_lines)
            
        except Exception as e:
            return f"Error generating code: {e}"

    def _create_team_slug(self, team_name: str) -> str:
        """
        Create a URL-friendly slug from a team name
        
        Args:
            team_name: Team name (e.g., "Boston Celtics")
            
        Returns:
            URL-friendly slug (e.g., "Boston-Celtics")
        """
        # Replace spaces with hyphens and remove special characters
        slug = team_name.replace(' ', '-')
        # Remove any remaining special characters except hyphens
        slug = re.sub(r'[^a-zA-Z0-9\-]', '', slug)
        return slug

    def get_league_depth_charts(self,
                               league_id: int,
                               league_name: str,
                               season: str = "2025",
                               output_file: Optional[str] = None) -> Dict:
        """
        Get depth charts for all teams in a league and optionally save to file
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            season: Season year
            output_file: Optional output file path for JSON export
            
        Returns:
            Dictionary containing league info and all team depth charts
        """
        return self.depth_chart_scraper.get_league_depth_charts(
            league_id=league_id,
            league_name=league_name,
            season=season,
            output_file=output_file
        )
    
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
            Dictionary containing roster data
        """
        return self.roster_scraper.get_team_roster(
            league_id=league_id,
            league_name=league_name,
            team_id=team_id,
            team_name=team_name,
            season=season
        )

    def get_league_rosters(self,
                          league_id: int,
                          league_name: str,
                          season: str = "2025",
                          output_file: Optional[str] = None) -> Dict:
        """
        Get rosters for all teams in a league and optionally save to file
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            season: Season year
            output_file: Optional output file path for JSON export
            
        Returns:
            Dictionary containing league info and all team rosters
        """
        return self.roster_scraper.get_league_rosters(
            league_id=league_id,
            league_name=league_name,
            season=season,
            output_file=output_file
        )

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
        return self.player_scraper.get_player_profile(player_id, player_name)

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
        return self.player_scraper.get_player_stats(player_id, player_name, league)

    def get_player(self, player_id: str, player_name: str, 
                   leagues: List[str] = ["International"]) -> Dict:
        """
        Get complete player information including profile and stats for specified leagues
        
        Args:
            player_id: Player ID from RealGM
            player_name: Player name slug (e.g., "Elijah-Stewart")
            leagues: List of leagues to fetch stats for (default: ["International"])
                    Supported leagues: ["International", "NBA", "WNBA", "D-League", "NCAA"]
            
        Returns:
            Dictionary containing player profile and stats for requested leagues:
            {
                'player_id': str,
                'name': str,
                'profile': Dict,
                'stats': Dict[str, pd.DataFrame]
            }
        """
        return self.player_scraper.get_player_stats_by_leagues(player_id, player_name, leagues)

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
        return self.player_scraper.get_league_players(league_name, season, team)

    def get_leagues(self, search_query: str = None) -> List[Dict[str, Union[int, str]]]:
        """
        Get list of all available basketball leagues or search for specific leagues

        Args:
            search_query: Optional search query to filter leagues

        Returns:
            List of dictionaries containing league information:
            [{'id': int, 'name': str}, ...]
        """
        from .leagues import BASKETBALL_LEAGUES, search_leagues

        if search_query:
            # Search for leagues matching the query
            matches = search_leagues(search_query)
            return [{'id': league_id, 'name': name} for league_id, name in matches]
        else:
            # Return all leagues
            return [{'id': league_id, 'name': name} for league_id, name in BASKETBALL_LEAGUES.items()]


# Example usage and helper functions
def create_api_client():
    """Factory function to create API client"""
    return RealGMStatsAPI()


# Constants for common values
STAT_TYPES = [
    "Averages", "Totals", "Per_48", "Per_40", "Per_36", 
    "Per_Minute", "Minute_Per", "Misc_Stats", "Advanced_Stats"
]

POSITIONS = ["All", "PG", "SG", "SF", "PF", "C"]

PROSPECTS = ["All", "Pro", "Draft"]

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


if __name__ == "__main__":
    # Example usage
    api = create_api_client()
    
    # Get stats for Romanian Divizia A
    print("Fetching Romanian Divizia A stats...")
    stats_df = api.get_league_stats(
        league_id=31,
        league_name="Romanian-Divizia-A",
        season="2025",
        stat_type="Averages",
        qualified=True,
        position="All"
    )
    
    print(f"Retrieved {len(stats_df)} player records")
    print("\nTop 5 scorers:")
    print(stats_df[['Player', 'Team', 'PPG']].head())
    
    # Get available filters
    print("\nFetching available filters...")
    filters = api.get_available_filters()
    for filter_name, options in filters.items():
        print(f"{filter_name}: {len(options)} options")
    
    # Get team list
    print("\nFetching team list...")
    teams = api.get_team_list()
    print(f"Found {len(teams)} teams")
    for team in teams[:5]:  # Show first 5 teams
        print(f"- {team['name']} (ID: {team['id']})")