from bs4 import BeautifulSoup
import requests
import json

# Get prematch odds for all ATP matches on current day
session = requests.Session()
odds_url = 'https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis/atp?lang=en&eventsLimit=50&preMatchOnly=true&marketFilterId=def'
odds_response = session.get(odds_url, headers={'User-Agent': 'Mozilla/5.0'})
odds_json = json.loads(odds_response.text)
data = []

def get_details(outcome):
    return {
        'name': outcome['description'],
        'odds': int(outcome['price']['american']),
    }

def get_outcomes(event):
    outcomes = event['displayGroups'][0]['markets'][1]['outcomes']
    return list(map(get_details, outcomes))

for tournament in odds_json:
    events = tournament['events']
    events_detailed = list(map(get_outcomes, events))
    data = data + events_detailed

print(data)

# Get probability that player 1 will win
url = 'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1=11127&playerId2=6269'
response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

doc = BeautifulSoup(response.text, 'html.parser')
win_prob_row = doc.find(text='Win Probability')
p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))

print(p1_win_prob)


# Calculate who to bet on

# sim_p1_wins = p1_win_prob * 10
# sim_p2_wins = 1000 - sim_p1_wins

# p1_win = sim_p1_wins * (100/odds[0])
# p1_lose = sim_p2_wins * -1
# p2_lose = sim_p1_wins * -1
# p2_win = sim_p2_wins * (odds[1]/100)

# p1_total = p1_win + p1_lose
# p2_total = p2_win + p2_lose

# if p1_total < 0 and p2_total < 0:
#     print('Do not bet')
# else:
#     if p1_total > p2_total:
#         print('Bet on player 1')
#     else:
#         print('Bet on player 2')

# print(p1_total)
# print(p2_total)
