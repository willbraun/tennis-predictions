from bs4 import BeautifulSoup
import requests
import json

url = 'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1=11127&playerId2=6269'

session = requests.Session()
response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

doc = BeautifulSoup(response.text, 'html.parser')
win_prob_row = doc.find(text='Win Probability')
p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))
print(p1_win_prob)

odds_session = requests.Session()
odds_url = "https://www.bovada.lv/services/sports/event/coupon/events/A/description/tennis?lang=en&eventsLimit=1"
odds_response = odds_session.get(odds_url, headers={'User-Agent': 'Mozilla/5.0'})
odds_json = json.loads(odds_response.text)
outcomes = odds_json[0]['events'][0]['displayGroups'][0]['markets'][1]['outcomes']

def get_american_odds(outcome):
    return outcome['price']['american']

odds = list(map(get_american_odds, outcomes))

print(odds)