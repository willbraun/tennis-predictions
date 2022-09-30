from bs4 import BeautifulSoup
from decouple import config
import requests
import json
import psycopg2
import datetime
import os


file_name = os.path.basename(__file__)

if file_name == 'index.py':
    db_table = config('DB_TABLE')
elif file_name == 'index_test.py':
    db_table = config('DB_TABLE_TEST')
else:
    raise Exception('Invalid filename')

print(datetime.datetime.now())

conn = psycopg2.connect(
    dbname=config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASS'),
    host=config('DB_HOST')
)

cur = conn.cursor()

def sql_command(statement):
    cur.execute(statement)
    conn.commit()

session = requests.Session()

def call_url(url):
    return session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Updating matches

def get_match_result(match):
    p1_name = match['TeamOne']['PlayerNameForUrl'].replace('-', ' ')
    p2_name = match['TeamTwo']['PlayerNameForUrl'].replace('-', ' ')
    
    return {
        'p1_name': p1_name, 
        'p2_name': p2_name,
        'winner': p1_name if int(match['Winner']) == 2 else p2_name,
    }

def get_all_match_results():
    url = 'https://www.atptour.com/-/ajax/Scores/GetInitialScores'
    response = call_url(url)
    match_results_json = json.loads(response.text)
    tournaments = match_results_json['liveScores']['Tournaments']
    data = []

    for tournament in tournaments:
        matches = tournament['Matches']
        completed = list(filter(lambda match: match['Status'] == 'F', matches))
        match_result = list(map(get_match_result, completed))
        data = data + match_result

    return data

def define_GBR():
    function_string = f"""
        CREATE OR REPLACE FUNCTION get_payout(odds INT)
        RETURNS FLOAT
        AS
        $$
        DECLARE
            payout FLOAT;
        BEGIN
            IF odds >= 0
                THEN SELECT odds/100.0 INTO payout;
                ELSE SELECT -100.0/odds INTO payout;
            END IF;
            RETURN payout;
        END
        $$

        LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION get_bet_result(p1_name VARCHAR(255), p2_name VARCHAR(255), winner VARCHAR(255))
        RETURNS FLOAT
        AS
        $$
        DECLARE
            decisionvalue INT;
            dbplayer1namevalue VARCHAR(255);
            dbplayer2namevalue VARCHAR(255);
            dbplayer1oddsvalue INT;
            dbplayer2oddsvalue INT;
        BEGIN
            SELECT 
                decision, player1name, player2name, player1odds, player2odds 
            FROM 
                {db_table} 
            INTO 
                decisionvalue, dbplayer1namevalue, dbplayer2namevalue, dbplayer1oddsvalue, dbplayer2oddsvalue
            WHERE 
                p1_name IN (player1name, player2name) AND p2_name IN (player1name, player2name) AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 172800000;
            
            IF decisionvalue = 0
                THEN RETURN 0;
            END IF;

            IF decisionvalue = 1	
                THEN 
                    IF winner = dbplayer1namevalue
                        THEN RETURN get_payout(dbplayer1oddsvalue);
                        ELSE RETURN -1;
                    END IF;
            END IF;

            IF decisionvalue = 2	
                THEN 
                    IF winner = dbplayer2namevalue
                        THEN RETURN get_payout(dbplayer2oddsvalue);
                        ELSE RETURN -1;
                    END IF;
            END IF;
        END;
        $$

        LANGUAGE plpgsql;

    """
    sql_command(function_string)

def update_match(match_result):
    p1 = match_result['p1_name']
    p2 = match_result['p2_name']
    winner = match_result['winner']

    update_string = f"""
        UPDATE 
            {db_table} 
        SET 
            betresult = get_bet_result('{p1}', '{p2}', '{winner}')
        WHERE 
            '{p1}' IN (player1name, player2name) AND '{p2}' IN (player1name, player2name) AND CAST(EXTRACT(epoch FROM NOW()) AS BIGINT)*1000 - startepoch < 172800000;
    """

    sql_command(update_string)

def update_completed_matches(match_results):
    define_GBR()
    for match in match_results:
        update_match(match)


result_data = get_all_match_results()
update_completed_matches(result_data)


# Inserting matches

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

    global prediction

    if p1_total < 0 and p2_total < 0:
         prediction = 0
    else:
        if p1_total > p2_total:
            prediction = 1
        else:
            prediction = 2

    return [p1_total, p2_total, prediction]

def convert_time(epoch):
    return datetime.datetime.fromtimestamp(epoch/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def create_row_string(event):
    [p1, p2, start_epoch, match_id] = unpack_event(event)
    p1_win_prob = get_win_prob(p1, p2)
    [p1_total, p2_total, prediction] = make_prediction(p1_win_prob, p1, p2)

    row_string = f"""(DEFAULT, '{p1['name']}', '{p2['name']}', {p1_win_prob}, {p1['odds']}, {p2['odds']}, {p1_total}, {p2_total}, {prediction}, {start_epoch}, {match_id}, '{convert_time(start_epoch)}')"""
    return row_string

def insert_new_matches(match_data):
    start_string = f"""INSERT INTO {db_table} (Id, Player1Name, Player2Name, Player1Prob, Player1Odds, Player2Odds, Player1Total, Player2Total, Decision, StartEpoch, MatchId, DateTimeUTC) VALUES """
    value_string = ', '.join(list(map(create_row_string, match_data)))
    where_string = ' ON CONFLICT (MatchId) DO NOTHING'
    insert_string = start_string + value_string + where_string + ';'
    sql_command(insert_string)


data = get_all_matches()
insert_new_matches(data)


cur.close()
conn.close()