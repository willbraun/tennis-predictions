import requests
from bs4 import BeautifulSoup

session = requests.Session()

p1_id = 4920 # Novak Djokovic
p2_id = 52602 # Carlos Alcaraz

# Web URL
url = f'https://www.ultimatetennisstatistics.com/headToHead?tab=hypotheticalMatchup&playerId1={p1_id}&playerId2={p2_id}'

# Internal API
# url = f'https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1={p1_id}&playerId2={p2_id}'


response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(response.text)

doc = BeautifulSoup(response.text, 'html.parser')
win_prob_row = doc.find(string='Win Probability')
print(win_prob_row)

# p1_win_prob = float(win_prob_row.parent.parent.find('h4').contents[0].replace('%', ''))
# print(p1_win_prob)


