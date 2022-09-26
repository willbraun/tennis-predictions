from bs4 import BeautifulSoup
from decouple import config
from datetime import datetime
import requests
import json
import psycopg2

conn = psycopg2.connect(
    dbname=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASS'),
    host=config('DB_HOST')
)

def sql_command(statement):
    cur = conn.cursor()
    cur.execute(statement)
    conn.commit()
    cur.close()
    conn.close()

# cur.execute("""ALTER TABLE matches DROP COLUMN IsCorrect""")

# cur.execute("""ALTER TABLE matches ADD COLUMN IsCorrect BOOLEAN""")


# cur.execute("""INSERT INTO matches (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, IsCorrect, BetResult) 
#                 VALUES (DEFAULT, 'Test Federer', 'Test Nadal', 60.0, -115, 110, 122.0, -160.0, 1, TRUE, 0.87)""")

# cur.execute('DELETE FROM matches WHERE id = 2')

# cur.execute('SELECT * FROM matches')

# print(cur.fetchall())

    

session = requests.Session()

def call_url(url):
    return session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Get prematch odds for all ATP matches on current day

def get_outcome_details(outcome):
    odds = outcome['price']['american']
    if odds == 'EVEN':
        odds = 0

    return {
        'name': outcome['description'],
        'odds': int(odds),
    }

def get_event_details(event):
    markets = event['displayGroups'][0]['markets']
    outcomes = list(filter(lambda x: x['description'] == 'Moneyline', markets))[0]['outcomes']
    start_epoch = event['startTime']
    match_id = event['id']

    return list(map(get_outcome_details, outcomes)) + [start_epoch, match_id]

def get_all_matches():
    url = 'https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis/atp?lang=en&eventsLimit=50&preMatchOnly=true&marketFilterId=def'
    response = call_url(url)
    matches_json = json.loads(response.text)
    data = []

    for tournament in matches_json:
        events = tournament['events']
        events_detailed = list(map(get_event_details, events))
        data = data + events_detailed

    return data

def get_id(name):
    term = name.replace(' ', '+').lower()
    search_url = f'https://www.ultimatetennisstatistics.com/autocompletePlayer?term={term}'
    search_response = call_url(search_url)
    search_json = json.loads(search_response.text)
    player = search_json[0]
    return player['id']

def unpack_event(event):
    [p1, p2, start_epoch, match_id] = event

    if p1['odds'] > p2['odds']:
        [p1, p2] = [p2, p1]

    return [p1, p2, start_epoch, match_id]

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

    global prediction

    if p1_total < 0 and p2_total < 0:
         prediction = 0
    else:
        if p1_total > p2_total:
            prediction = 1
        else:
            prediction = 2

    return [p1_total, p2_total, prediction]

def insert_match(event):
    [p1, p2, start_epoch, match_id] = unpack_event(event)
    p1_win_prob = get_win_prob(p1, p2)
    [p1_total, p2_total, prediction] = make_prediction(p1_win_prob, p1, p2)

    # cur.execute("""INSERT INTO matches (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, IsCorrect, BetResult) 
#                 VALUES (DEFAULT, 'Test Federer', 'Test Nadal', 60.0, -115, 110, 122.0, -160.0, 1, TRUE, 0.87)""")

    insert_string = f"""INSERT INTO matches (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, StartEpoch, MatchId) 
                        VALUES (DEFAULT, '{p1['name']}', '{p2['name']}', {p1_win_prob}, {p1['odds']}, {p2['odds']}, {p1_total}, {p2_total}, {prediction}, {start_epoch}, {match_id})"""
    
    sql_command(insert_string)

data = get_all_matches()
test_event = data[0]
# insert_match(test_event)


def get_match_result(match):
    p1 = match['TeamOne']
    p2 = match['TeamTwo']

    global result

    if p1['TeamStatus'] == 'won-game':
        result = 1
    if p2['TeamStatus'] == 'won-game':
        result = 2

    if bool(result):
        return {
            'p1_name': p1['PlayerNameForUrl'].replace('-', ' '), 
            'p2_name': p2['PlayerNameForUrl'].replace('-', ' '),
            'winner': result,
        }
    else:
        raise Exception(f"No winner found for{match}")

def get_match_results():
    url = 'https://www.atptour.com/-/ajax/Scores/GetInitialScores'
    response = call_url(url)
    match_results_json = json.loads(response.text)
    tournaments = match_results_json['liveScores']['Tournaments']
    data = []

    for tournament in tournaments:
        matches = tournament['Matches']
        match_result = list(map(get_match_result, matches))
        data = data + match_result

    return data
    

result_data = get_match_results()

# def update_match_winner(match_result):

