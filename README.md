# Overview

I built this to practice web scraping and simulate bets on tennis matches. Index.py scrapes a match prediction and betting odds from the web to simulate a bet. After the match occurs, it updates my database with the result and calculates the simulated payout.

Check out my detailed blog post about this project [here](https://blog.willbraun.dev/how-i-tried-to-get-rich-using-web-scraping).

## Usage

I have a PostGreSQL database set up locally, and I use launchd from my computer to run index.py periodically. I can then run get_result.py to print out the rate of return of my simulated bets. To set up something similar, you will need to create a PostGreSQL database and import your credentials to util.py.

## Technologies used

Python, BeautifulSoup, SQL, PLpgSQL, PostgreSQL, launchd
