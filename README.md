# Overview

The purpose of this project is to practice web scraping and simulate bets on tennis matches. Index.py scrapes a match prediction and betting odds from the web to simulate a bet. After the match occurs, it updates my database with the result and calculates the simulated payout.

## Usage

I have a PostGresSQL database set up locally, and I use launchd from my computer to run index.py periodically. I then run get_result.py to print out the rate of return of my simulated bets.

## Technologies used

Python, BeautifulSoup, SQL, PLpgSQL, PostgreSQL, launchd
