from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup

import json


#constants
REMOTE_HOST="http://35.238.5.118"
USERNAME='userexam'
PASSWORD='11111111'

if __name__ == '__main__':

  opts = Options()
  opts.headless = True
  assert opts.headless

  browser = Firefox(options=opts)
  browser.get(REMOTE_HOST)
  wait = WebDriverWait(browser, 10)

  assert "ninepine" in browser.title.lower()
  
  # login    
  username_el=browser.find_element(By.XPATH, '//*[@id="username"]')
  password_el=browser.find_element(By.XPATH, '//*[@id="password"]')
  username_el.clear()
  password_el.clear()
  username_el.send_keys(USERNAME)
  password_el.send_keys(PASSWORD)
  password_el.send_keys(Keys.RETURN) #simulate ENTER key after entering password

  WebDriverWait(browser, 10).until(lambda browser: browser.find_element_by_xpath('//*[@id="sidebar"]/div'))

  data = {}
  # extract sidebar data
  data["maximum_bet"]=browser.find_element(By.XPATH, '//*[@id="sidebar"]/div/span[2]').text
  data["availabe_balance"]=browser.find_element(By.XPATH, '//*[@id="sidebar"]/div/span[4]').text
  # data["open_bets"]=browser.find_element(By.XPATH, '//*[@id="sidebar"]/div/span[6]').text

  print("sidebar data:\n {}".format(json.dumps(data, indent=2)))

  # execute javascript to load data into iframe
  browser.execute_script("angular.element($('#frame-trade')).scope().generateTrade();")

  dtframe = '//*[@id="frame-trade"]'
  # switch to iframe
  browser.switch_to.frame(browser.find_element(By.XPATH, dtframe))

  # use bs4 for parsing rendered html
  page = BeautifulSoup(browser.page_source, "lxml")

  # parse data table
  cards = page.select('div[class="card"]')
  data_table=[]
  for card in cards:
      table = card.find('table')
      rows = table.find_all('tr')
      match_name = rows[0].find_all('th')[0].find('span').text
      r1_tds = rows[1].find_all('td')
      r2_tds = rows[2].find_all('td')
      player_name_home = r1_tds[1].find('span', class_="player-name-home").text
      player_score_home = r1_tds[1].find('span', class_="player-score-home").text
      player_name_away = r1_tds[1].find('span', class_="player-name-away").text
      player_away_score = r1_tds[1].find('span', class_="player-score-away").text
      bet_time = r2_tds[1].find('span').text
      
      scores = []
      for i, s in enumerate(r1_tds):
          if i == 0:
              continue
          attrib = s.get("data-var")
          if attrib:
              k = attrib.replace('soc_col_','')
              scores.append({k: s.text})

      data_table.append({
            "match": match_name,
            "player_name_home": str(player_name_home),
            "player_score_home": str(player_score_home),
            "player_name_away": str(player_name_away),
            "player_away_score": str(player_away_score),
            "bet_time": str(bet_time),
            "scores": scores
      })
  print("data table:\n {}".format(json.dumps(data_table, indent=2)))

  browser.quit()