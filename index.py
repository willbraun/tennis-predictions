from bs4 import BeautifulSoup
from decouple import config
import requests
import json

import psycopg2

conn = psycopg2.connect(
    dbname=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASS'),
    host=config('DB_HOST')
)

cur = conn.cursor()

# cur.execute("""select *
# from INFORMATION_SCHEMA.COLUMNS
# where TABLE_NAME='matches'""")

cur.execute('SELECT * FROM matches')

# cur.execute('INSERT INTO matches (Id) VALUES (1)')

print(cur.fetchall())

# cur.execute("""CREATE TABLE matches (
#     Id SERIAL PRIMARY KEY,
#     Player1Name VARCHAR(255),
#     Player2Name VARCHAR(255),
#     Player1Prob FLOAT,
#     Player1Odds INT,
#     Player2Odds INT,
#     Player1Total FLOAT,
#     Player2Total FLOAT,
#     Decision INT,
#     IsCorrect BIT,
#     BetResult FLOAT
#     )""")

conn.commit()

cur.close()
conn.close()

session = requests.Session()

def call_url(url):
    return session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Get prematch odds for all ATP matches on current day

odds_url = 'https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis/atp?lang=en&eventsLimit=50&preMatchOnly=true&marketFilterId=def'
odds_response = call_url(odds_url)
odds_json = json.loads(odds_response.text)
data = []

def get_details(outcome):
    odds = outcome['price']['american']
    if odds == 'EVEN':
        odds = 0

    return {
        'name': outcome['description'],
        'odds': int(odds),
    }

def get_outcomes(event):
    markets = event['displayGroups'][0]['markets']
    outcomes = list(filter(lambda x: x['description'] == 'Moneyline', markets))[0]['outcomes']

    return list(map(get_details, outcomes))

for tournament in odds_json:
    events = tournament['events']
    events_detailed = list(map(get_outcomes, events))
    data = data + events_detailed

# print(data)

# Get UTS id based on the player name
def get_id(name):
    term = name.replace(' ', '+').lower()
    search_url = f'https://www.ultimatetennisstatistics.com/autocompletePlayer?term={term}'
    search_response = call_url(search_url)
    search_json = json.loads(search_response.text)
    player = search_json[0]
    return player['id']

# Get probability that player 1 will win for single event
test_event = data[0]

[p1, p2] = test_event

if p1['odds'] > p2['odds']:
    [p1, p2] = [p2, p1]

print(p1, p2)
p1_id = get_id(p1['name'])
p2_id = get_id(p2['name'])

prob_url = f'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1={p1_id}&playerId2={p2_id}'
prob_response = call_url(prob_url)

doc = BeautifulSoup(prob_response.text, 'html.parser')
win_prob_row = doc.find(text='Win Probability')
p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))

print(p1_win_prob)


# Calculate who to bet on

sim_p1_wins = p1_win_prob * 10
sim_p2_wins = 1000 - sim_p1_wins

def get_factor(odds):
    if odds > 0:
        return abs(odds)/100
    else:
        return 100/abs(odds)

p1_win = sim_p1_wins * get_factor(p1['odds'])
p1_lose = sim_p2_wins * -1
p2_lose = sim_p1_wins * -1
p2_win = sim_p2_wins * get_factor(p2['odds'])

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
