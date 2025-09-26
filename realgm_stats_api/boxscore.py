import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urljoin

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

class BoxscoreScraper:
    """Scraper for RealGM boxscore data"""
    def __init__(self, session: requests.Session, base_url: str, rate_limit: float = 1.0):
        self.session = session
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.league_slugs = {
            31: "Romanian-Divizia-A",
            50: "French-LNB-Pro-B",
            54: "Italian-Serie-A2-Basket",
        }

    def get_game_dates(self, league_id: int, league_name: str = None) -> List[str]:
        """
        Get available game dates for a league
        
        Args:
            league_id: League ID (not used for major leagues)
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of date strings in YYYY-MM-DD format
        """
        if league_name and _is_major_league(league_name):
            # Major leagues use different endpoint
            url = urljoin(self.base_url, f"/ajax/{league_name.lower()}_scoreboard.phtml")
            params = {'action': 'showdates'}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            date_arrays = response.json()
            dates = [f"{year:04d}-{month:02d}-{day:02d}" for month, day, year in date_arrays]
            return sorted(dates)
        else:
            # International leagues use the original endpoint
            url = urljoin(self.base_url, "/ajax/international_scoreboard.phtml")
            params = {'action': 'showdates', 'leagueid': league_id}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            date_arrays = response.json()
            dates = [f"{year:04d}-{month:02d}-{day:02d}" for month, day, year in date_arrays]
            return sorted(dates)

    def get_boxscore_links(self, league_id: int, date: str, league_name: str = None) -> List[Dict[str, str]]:
        """
        Get boxscore links for games on a specific date
        
        Args:
            league_id: League ID (not used for major leagues)
            date: Date string in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of game dictionaries with boxscore information
        """
        if league_name and _is_major_league(league_name):
            # Major leagues use simple URL pattern
            url = urljoin(self.base_url, f"/{league_name.lower()}/scores/{date}")
        else:
            # International leagues use the complex URL pattern
            league_slug = self.league_slugs.get(league_id, f"league-{league_id}")
            url = urljoin(self.base_url, f"/international/league/{league_id}/{league_slug}/scores/{date}")
        
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []
        
        # Find all game tables
        game_tables = soup.find_all('table', class_='game')
        for game_table in game_tables:
            # Check if this game has a boxscore available (skip PREVIEW games)
            preview_button = game_table.find(string="PREVIEW")
            if preview_button:
                continue  # Skip games that only have PREVIEW button

            # Get team information
            team_details = game_table.find_all('div', class_='team_name')
            team_records = game_table.find_all('div', class_='team_record')
            team_scores = game_table.find_all('div', class_='team_score')

            if len(team_details) >= 2 and len(team_records) >= 2 and len(team_scores) >= 2:
                # Check if team scores have boxscore links (additional safety check)
                away_score_link = team_scores[0].find('a')
                if not away_score_link:
                    continue  # Skip if no boxscore link available

                # Get away team info
                away_team = team_details[0].find('a').text.strip()
                away_record = team_records[0].find('a').text.strip('()')
                away_score = away_score_link.text.strip()

                # Get home team info
                home_team = team_details[1].find('a').text.strip()
                home_record = team_records[1].find('a').text.strip('()')

                # Handle home score - it might be in team_scores[1] or team_scores[2]
                home_score = None
                if len(team_scores) >= 3:
                    home_score_link = team_scores[2].find('a')
                    if home_score_link:
                        home_score = home_score_link.text.strip()

                if not home_score and len(team_scores) >= 2:
                    home_score_link = team_scores[1].find('a')
                    if home_score_link:
                        home_score = home_score_link.text.strip()

                if not home_score:
                    continue  # Skip if we can't find home team score

                # Get boxscore link
                boxscore_link = away_score_link['href']
                game_id = boxscore_link.split('/')[-1]
                
                games.append({
                    'url': urljoin(self.base_url, boxscore_link),
                    'game_id': game_id,
                    'date': date,
                    'away_team': away_team,
                    'away_record': away_record,
                    'away_score': away_score,
                    'home_team': home_team,
                    'home_record': home_record,
                    'home_score': home_score
                })
        
        return games

    def get_upcoming_games(self, league_id: int, date: str, league_name: str = None) -> List[Dict[str, str]]:
        """
        Get upcoming games for a specific date
        
        Args:
            league_id: League ID (not used for major leagues)
            date: Date string in YYYY-MM-DD format
            league_name: League name slug (e.g., "nba", "wnba", "Romanian-Divizia-A")
            
        Returns:
            List of upcoming game dictionaries with game information
        """
        if league_name and _is_major_league(league_name):
            # Major leagues use simple URL pattern
            url = urljoin(self.base_url, f"/{league_name.lower()}/scores/{date}")
        else:
            # International leagues use the complex URL pattern
            league_slug = self.league_slugs.get(league_id, f"league-{league_id}")
            url = urljoin(self.base_url, f"/international/league/{league_id}/{league_slug}/scores/{date}")
        
        response = self.session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []
        
        # Find all unplayed game tables - use more flexible selector
        game_tables = soup.find_all('table', class_=['game', 'force-table', 'unplayed'])
        for game_table in game_tables:
            # Additional check to ensure it has all required classes
            classes = game_table.get('class', [])
            if 'game' in classes and 'force-table' in classes and 'unplayed' in classes:
                game_info = self._parse_upcoming_game_table(game_table, date)
                if game_info:
                    games.append(game_info)
        
        return games

    def _parse_upcoming_game_table(self, table, date: str) -> Optional[Dict[str, str]]:
        """
        Parse an upcoming game table to extract game information
        
        Args:
            table: BeautifulSoup table element
            date: Date string in YYYY-MM-DD format
            
        Returns:
            Dictionary with game information or None if parsing fails
        """
        try:
            # Get team information from the first row
            team_details = table.find_all('div', class_='team_name')
            if len(team_details) < 2:
                return None
            
            away_team = team_details[0].find('a').text.strip()
            home_team = team_details[1].find('a').text.strip()
            
            # Get time information
            time_cell = table.find('td', style=lambda x: x and 'text-align: center' in x and 'font-size: 1em' in x)
            time_text = ""
            if time_cell:
                time_span = time_cell.find('span', style=lambda x: x and 'font-size: 1.4em' in x)
                if time_span:
                    time_text = time_span.text.strip()
            
            # Get location information from the second row
            location = ""
            game_type = ""
            game_stats_row = table.find('tr', class_='game_stats')
            if game_stats_row:
                th_elements = game_stats_row.find_all('th')
                if len(th_elements) >= 2:
                    # Location is in the first th
                    location_link = th_elements[0].find('a')
                    if location_link:
                        location = location_link.text.strip()
                    
                    # Game type is in the second th
                    game_type = th_elements[1].text.strip()
            
            return {
                'date': date,
                'time': time_text,
                'home': home_team,
                'away': away_team,
                'location': location,
                'type': game_type
            }
        except Exception as e:
            # Log error and return None for this game
            print(f"Error parsing upcoming game table: {e}")
            return None

    def parse_boxscore(self, game_info: Dict[str, str]) -> Dict:
        response = self.session.get(game_info['url'])
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        game_data = {
            'game_id': game_info['game_id'],
            'date': game_info['date'],
            'url': game_info['url'],
            'away_team': game_info['away_team'],
            'home_team': game_info['home_team'],
            'scraped_at': datetime.now().isoformat()
        }
        all_tables = soup.find_all('table')
        table_index = 0
        if table_index < len(all_tables):
            game_data['scores'] = self._parse_score_table(all_tables[table_index])
            table_index += 1
        if table_index < len(all_tables):
            game_data['advanced_stats'] = self._parse_advanced_table(all_tables[table_index])
            table_index += 1
        if table_index < len(all_tables):
            game_data['four_factors'] = self._parse_four_factors_table(all_tables[table_index])
            table_index += 1
        game_data['player_stats'] = {}
        game_data['depth_charts'] = {}
        h2_tags = soup.find_all('h2')
        for h2 in h2_tags:
            h2_text = h2.text.strip()
            if 'Depth Chart' not in h2_text:
                team_name = h2_text
                next_elem = h2.find_next_sibling()
                while next_elem:
                    if next_elem.name == 'table':
                        headers = [th.text.strip() for th in next_elem.find_all('th')]
                        if 'Player' in headers and 'PTS' in headers:
                            team_key = self._determine_team_key(team_name, game_data)
                            if team_key:
                                game_data['player_stats'][team_key] = self._parse_player_stats_table(next_elem)
                        break
                    next_elem = next_elem.find_next_sibling()
            else:
                team_name = h2_text.replace(' Depth Chart', '').strip()
                next_table = h2.find_next('table')
                if next_table:
                    team_key = self._determine_team_key(team_name, game_data)
                    if team_key:
                        game_data['depth_charts'][team_key] = self._parse_depth_chart_table(next_table)
        game_data['metadata'] = self._extract_metadata(soup)
        return game_data

    def _determine_team_key(self, team_name: str, game_data: Dict) -> Optional[str]:
        # Check exact matches first
        if team_name == game_data.get('away_team'):
            return 'away'
        elif team_name == game_data.get('home_team'):
            return 'home'
        
        # Check if team name contains the short name (for WNBA cases like "Washington Mystics" vs "Washington")
        if game_data.get('away_team') and game_data.get('away_team') in team_name:
            return 'away'
        elif game_data.get('home_team') and game_data.get('home_team') in team_name:
            return 'home'
        
        # Check if short name contains the team name (reverse check)
        if team_name in game_data.get('away_team', ''):
            return 'away'
        elif team_name in game_data.get('home_team', ''):
            return 'home'
        
        # Handle common WNBA name variations
        team_variations = {
            'Los Angeles Sparks': ['L.A. Sparks', 'LA Sparks', 'Los Angeles'],
            'L.A. Sparks': ['Los Angeles Sparks', 'LA Sparks', 'Los Angeles'],
            'LA Sparks': ['Los Angeles Sparks', 'L.A. Sparks', 'Los Angeles'],
            'Washington Mystics': ['Washington'],
            'Connecticut Sun': ['Connecticut'],
            'Seattle Storm': ['Seattle'],
            'Minnesota Lynx': ['Minnesota'],
            'Phoenix Mercury': ['Phoenix'],
            'Indiana Fever': ['Indiana'],
            'Chicago Sky': ['Chicago'],
            'Atlanta Dream': ['Atlanta'],
            'New York Liberty': ['New York'],
            'Dallas Wings': ['Dallas'],
            'Las Vegas Aces': ['Las Vegas'],
            'Golden State Valkyries': ['Golden State']
        }
        
        # Check if the team name from HTML matches any variation of away team
        away_team = game_data.get('away_team', '')
        if away_team in team_variations:
            if team_name in team_variations[away_team] or team_name == away_team:
                return 'away'
        elif team_name in team_variations:
            if away_team in team_variations[team_name] or team_name == away_team:
                return 'away'
        
        # Check if the team name from HTML matches any variation of home team
        home_team = game_data.get('home_team', '')
        if home_team in team_variations:
            if team_name in team_variations[home_team] or team_name == home_team:
                return 'home'
        elif team_name in team_variations:
            if home_team in team_variations[team_name] or team_name == home_team:
                return 'home'
        
        # Check against team abbreviations from scores
        if 'scores' in game_data:
            if team_name == game_data['scores'].get('away_abbr'):
                return 'away'
            elif team_name == game_data['scores'].get('home_abbr'):
                return 'home'
        
        return None

    def _parse_score_table(self, table) -> Dict:
        scores = {'quarters': {}, 'final': {}}
        headers = [th.text.strip() for th in table.find_all('th')]
        rows = table.find_all('tr')
        data_rows = [row for row in rows if row.find('td')]
        if len(data_rows) >= 2:
            away_cells = [td.text.strip() for td in data_rows[0].find_all('td')]
            home_cells = [td.text.strip() for td in data_rows[1].find_all('td')]
            if away_cells and home_cells:
                away_info = away_cells[0]
                home_info = home_cells[0]
                away_match = re.match(r'(\w+)\s*\(([^)]+)\)', away_info)
                home_match = re.match(r'(\w+)\s*\(([^)]+)\)', home_info)
                if away_match:
                    scores['away_abbr'] = away_match.group(1)
                    scores['away_record'] = away_match.group(2)
                else:
                    scores['away_abbr'] = away_info.split()[0] if away_info else ''
                if home_match:
                    scores['home_abbr'] = home_match.group(1)
                    scores['home_record'] = home_match.group(2)
                else:
                    scores['home_abbr'] = home_info.split()[0] if home_info else ''
                for i, header in enumerate(headers[1:], 1):
                    if i < len(away_cells) and i < len(home_cells):
                        if header in ['1', '2', '3', '4']:
                            scores['quarters'][f'Q{header}_away'] = int(away_cells[i])
                            scores['quarters'][f'Q{header}_home'] = int(home_cells[i])
                        elif header == 'OT':
                            scores['quarters']['OT_away'] = int(away_cells[i])
                            scores['quarters']['OT_home'] = int(home_cells[i])
                        elif header == 'Final':
                            scores['final']['away'] = int(away_cells[i])
                            scores['final']['home'] = int(home_cells[i])
        return scores

    def _parse_advanced_table(self, table) -> Dict:
        advanced = {}
        rows = table.find_all('tr')
        data_rows = [row for row in rows if row.find('td')]
        if len(data_rows) >= 2:
            away_cells = [td.text.strip() for td in data_rows[0].find_all('td')]
            home_cells = [td.text.strip() for td in data_rows[1].find_all('td')]
            if len(away_cells) >= 4 and len(home_cells) >= 4:
                advanced['possessions'] = int(away_cells[1])
                advanced['away_offensive_rating'] = float(away_cells[2])
                advanced['away_defensive_rating'] = float(away_cells[3])
                advanced['home_offensive_rating'] = float(home_cells[2])
                advanced['home_defensive_rating'] = float(home_cells[3])
        return advanced

    def _parse_four_factors_table(self, table) -> Dict:
        four_factors = {}
        rows = table.find_all('tr')
        data_rows = [row for row in rows if row.find('td')]
        if len(data_rows) >= 2:
            away_cells = [td.text.strip() for td in data_rows[0].find_all('td')]
            home_cells = [td.text.strip() for td in data_rows[1].find_all('td')]
            if len(away_cells) >= 5 and len(home_cells) >= 5:
                four_factors['away_efg_pct'] = float(away_cells[1])
                four_factors['away_to_pct'] = float(away_cells[2])
                four_factors['away_or_pct'] = float(away_cells[3])
                four_factors['away_ftr'] = float(away_cells[4])
                four_factors['home_efg_pct'] = float(home_cells[1])
                four_factors['home_to_pct'] = float(home_cells[2])
                four_factors['home_or_pct'] = float(home_cells[3])
                four_factors['home_ftr'] = float(home_cells[4])
        return four_factors

    def _parse_player_stats_table(self, table) -> Dict:
        result = {'players': [], 'totals': {}}
        headers = [th.text.strip() for th in table.find_all('th')]
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    player = self._parse_player_row(cells, headers)
                    if player and 'name' in player:
                        result['players'].append(player)
        tfoot = table.find('tfoot')
        if tfoot:
            totals_rows = tfoot.find_all('tr', class_='stattotals')
            if len(totals_rows) >= 2:
                cells = totals_rows[1].find_all(['th', 'td'])
                if len(cells) >= 18:
                    result['totals'] = {
                        'minutes': cells[4].text.strip(),
                        'fgm_a': cells[5].text.strip(),
                        'three_pm_a': cells[6].text.strip(),
                        'ftm_a': cells[7].text.strip(),
                        'fic': float(cells[8].text.strip()) if cells[8].text.strip() else 0,
                        'offensive_rebounds': int(cells[9].text.strip()) if cells[9].text.strip().isdigit() else 0,
                        'defensive_rebounds': int(cells[10].text.strip()) if cells[10].text.strip().isdigit() else 0,
                        'total_rebounds': int(cells[11].text.strip()) if cells[11].text.strip().isdigit() else 0,
                        'assists': int(cells[12].text.strip()) if cells[12].text.strip().isdigit() else 0,
                        'personal_fouls': int(cells[13].text.strip()) if cells[13].text.strip().isdigit() else 0,
                        'steals': int(cells[14].text.strip()) if cells[14].text.strip().isdigit() else 0,
                        'turnovers': int(cells[15].text.strip()) if cells[15].text.strip().isdigit() else 0,
                        'blocks': int(cells[16].text.strip()) if cells[16].text.strip().isdigit() else 0,
                        'points': int(cells[17].text.strip()) if cells[17].text.strip().isdigit() else 0
                    }
                if len(totals_rows) >= 3:
                    pct_cells = totals_rows[2].find_all(['th', 'td'])
                    if len(pct_cells) >= 8:
                        result['totals']['fg_percentage'] = pct_cells[5].text.strip()
                        result['totals']['three_percentage'] = pct_cells[6].text.strip()
                        result['totals']['ft_percentage'] = pct_cells[7].text.strip()
        return result

    def _parse_player_row(self, cells, headers) -> Dict:
        player = {}
        for i, header in enumerate(headers):
            if i >= len(cells):
                continue
            cell = cells[i]
            value = cell.text.strip()
            if header == '#':
                player['number'] = value if value != '-' else None
            elif header == 'Player':
                link = cell.find('a')
                if link:
                    player['name'] = link.text.strip()
                    player['player_id'] = link.get('href', '').split('/')[-1]
                else:
                    player['name'] = value
            elif header == 'Status':
                player['is_starter'] = value == 'Starter'
                player['status'] = value
            elif header == 'Pos':
                player['position'] = value
            elif header == 'Min':
                player['minutes'] = value
            elif header == 'FGM-A':
                if '-' in value:
                    made, attempted = value.split('-')
                    player['fg_made'] = int(made)
                    player['fg_attempted'] = int(attempted)
            elif header == '3PM-A':
                if '-' in value:
                    made, attempted = value.split('-')
                    player['three_made'] = int(made)
                    player['three_attempted'] = int(attempted)
            elif header == 'FTM-A':
                if '-' in value:
                    made, attempted = value.split('-')
                    player['ft_made'] = int(made)
                    player['ft_attempted'] = int(attempted)
            elif header == 'FIC':
                try:
                    player['fic'] = float(value)
                except:
                    player['fic'] = 0.0
            elif header == 'Off':
                player['offensive_rebounds'] = int(value) if value.isdigit() else 0
            elif header == 'Def':
                player['defensive_rebounds'] = int(value) if value.isdigit() else 0
            elif header == 'Reb':
                player['total_rebounds'] = int(value) if value.isdigit() else 0
            elif header == 'Ast':
                player['assists'] = int(value) if value.isdigit() else 0
            elif header == 'PF':
                player['personal_fouls'] = int(value) if value.isdigit() else 0
            elif header == 'STL':
                player['steals'] = int(value) if value.isdigit() else 0
            elif header == 'TO':
                player['turnovers'] = int(value) if value.isdigit() else 0
            elif header == 'BLK':
                player['blocks'] = int(value) if value.isdigit() else 0
            elif header == 'PTS':
                player['points'] = int(value) if value.isdigit() else 0
        return player

    def _parse_depth_chart_table(self, table) -> Dict:
        depth_chart = {}
        rows = table.find_all('tr')
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            role_cell = cells[0]
            role_text = role_cell.text.strip()
            strong = role_cell.find('strong')
            if strong:
                role = strong.text.strip()
            else:
                role = role_text
            if role in ['Starters', 'Rotation', 'Lim PT']:
                role_key = role.lower().replace(' ', '_')
                depth_chart[role_key] = {}
                for i, pos in enumerate(positions):
                    if i + 1 < len(cells):
                        cell = cells[i + 1]
                        link = cell.find('a')
                        if link:
                            cell_text = cell.get_text('\n', strip=True)
                            lines = cell_text.split('\n')
                            player_info = {
                                'name': link.text.strip(),
                                'player_id': link.get('href', '').split('/')[-1]
                            }
                            if len(lines) > 1:
                                player_info['season_stats'] = lines[1]
                            depth_chart[role_key][pos] = player_info
        return depth_chart

    def _extract_metadata(self, soup) -> Dict:
        metadata = {}
        for elem in soup.find_all(text=True):
            text = elem.strip()
            if 'Attendance:' in text:
                match = re.search(r'Attendance:\s*(\d+)', text)
                if match:
                    metadata['attendance'] = int(match.group(1))
            elif 'Officials:' in text:
                officials = text.split('Officials:')[1].strip()
                if officials and officials != 'N/A':
                    metadata['officials'] = officials
        return metadata 