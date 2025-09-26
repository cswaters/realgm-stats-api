# Tests

This directory contains test scripts for the RealGM Stats API.

## Test Files

- `test_boxscores_major.py` - Tests for major league (NBA/WNBA) boxscore functionality
- `test_major_boxscores_real.py` - Real-world tests with major league data
- `test_wnba_parsing.py` - WNBA-specific parsing tests
- `test_league_players.py` - League player listing tests
- `test_player.py` - Individual player data tests

## Running Tests

Run tests from the project root:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_boxscores_major.py

# Run with verbose output
python -m pytest tests/ -v
```

## Requirements

Make sure you have pytest installed:

```bash
pip install pytest
```