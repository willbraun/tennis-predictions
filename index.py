from bs4 import BeautifulSoup
import requests

url = "https://www.ultimatetennisstatistics.com/h2hHypotheticalMatchup?playerId1=11127&playerId2=6269"

session = requests.Session()
response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

doc = BeautifulSoup(response.text, "html.parser")
win_prob_row = doc.find(text="Win Probability")
p1_win_prob = float(win_prob_row.parent.parent.find("h4").contents[0].replace("%", ''))
print(p1_win_prob)