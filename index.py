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

# cur.execute("""ALTER TABLE matches DROP COLUMN IsCorrect""")

# cur.execute("""ALTER TABLE matches ADD COLUMN IsCorrect BOOLEAN""")


# cur.execute("""INSERT INTO matches (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, IsCorrect, BetResult) 
#                 VALUES (DEFAULT, 'Test Federer', 'Test Nadal', 60.0, -115, 110, 122.0, -160.0, 1, TRUE, 0.87)""")

# cur.execute('DELETE FROM matches WHERE id = 2')

# cur.execute('SELECT * FROM matches')

# print(cur.fetchall())

conn.commit()

cur.close()
conn.close()

session = requests.Session()

def call_url(url):
    return session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Get prematch odds for all ATP matches on current day

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

def get_all_matches():
    url = 'https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis/atp?lang=en&eventsLimit=50&preMatchOnly=true&marketFilterId=def'
    response = call_url(url)
    matches_json = json.loads(response.text)
    data = []

    for tournament in matches_json:
        events = tournament['events']
        events_detailed = list(map(get_outcomes, events))
        data = data + events_detailed

    return data

data = get_all_matches()

def get_id(name):
    term = name.replace(' ', '+').lower()
    search_url = f'https://www.ultimatetennisstatistics.com/autocompletePlayer?term={term}'
    search_response = call_url(search_url)
    search_json = json.loads(search_response.text)
    player = search_json[0]
    return player['id']

def get_players(event):
    [p1, p2] = event

    if p1['odds'] > p2['odds']:
        [p1, p2] = [p2, p1]

    return [p1, p2]

def get_win_prob(p1, p2):
    p1_id = get_id(p1['name'])
    p2_id = get_id(p2['name'])

    prob_url = f'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1={p1_id}&playerId2={p2_id}'
    prob_response = call_url(prob_url)

    doc = BeautifulSoup(prob_response.text, 'html.parser')
    win_prob_row = doc.find(text='Win Probability')
    p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))
    print(p1_win_prob)
    return p1_win_prob

def get_factor(odds):
    if odds >= 0:
        return abs(odds)/100
    else:
        return 100/abs(odds)

def make_prediction(p1_win_prob, p1, p2):
    sim_p1_wins = p1_win_prob * 10
    sim_p2_wins = 1000 - sim_p1_wins

    p1_win = sim_p1_wins * get_factor(p1['odds'])
    p1_lose = sim_p2_wins * -1
    p2_lose = sim_p1_wins * -1
    p2_win = sim_p2_wins * get_factor(p2['odds'])

    p1_total = p1_win + p1_lose
    p2_total = p2_win + p2_lose

    print(p1_total)
    print(p2_total)

    if p1_total < 0 and p2_total < 0:
        return 0
    else:
        if p1_total > p2_total:
            return 1
        else:
            return 2

def process_event(event):
    [p1, p2] = get_players(event)
    p1_win_prob = get_win_prob(p1, p2)

    prediction = make_prediction(p1_win_prob, p1, p2)



test_event = data[0]
process_event(test_event)
