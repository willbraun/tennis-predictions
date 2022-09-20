from bs4 import BeautifulSoup
import requests
import json

# Get odds for the first match on the list (to change)
session = requests.Session()
odds_url = "https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis?lang=en&eventsLimit=1"
odds_response = session.get(odds_url, headers={'User-Agent': 'Mozilla/5.0'})
odds_json = json.loads(odds_response.text)
outcomes = odds_json[0]['events'][0]['displayGroups'][0]['markets'][1]['outcomes']

def get_american_odds(outcome):
    return int(outcome['price']['american'])

odds = list(map(get_american_odds, outcomes))

print(odds)

# Get probability that player 1 will win
url = 'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1=11127&playerId2=6269'
response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

doc = BeautifulSoup(response.text, 'html.parser')
win_prob_row = doc.find(text='Win Probability')
p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))

print(p1_win_prob)


# Calculate who to bet on
sim_p1_wins = p1_win_prob * 10
sim_p2_wins = 1000 - sim_p1_wins

p1_win = sim_p1_wins * (100/odds[0])
p1_lose = sim_p2_wins * -1
p2_lose = sim_p1_wins * -1
p2_win = sim_p2_wins * (odds[1]/100)

p1_total = p1_win + p1_lose
p2_total = p2_win + p2_lose

if p1_total < 0 and p2_total < 0:
    print('Do not bet')
else:
    if p1_total > p2_total:
        print('Bet on player 1')
    else:
        print('Bet on player 2')

print(p1_total)
print(p2_total)
