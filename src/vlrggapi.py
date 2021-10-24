import bs4
import logging
import json
import requests
from requests.api import request
from datetime import date, datetime


logging.basicConfig(level=logging.DEBUG)

BASE = "https://www.vlr.gg/"
MATCHES = "matches/"
RANKINGS = "rankings/"
NEWS = "news/"
FORUMS = "forum/"
PLAYER = "player/"

def rm_tabs_newlines(string):
    string = string.replace("\n", "") #eliminates newlines 
    string = string.replace("\t", "") #eliminates tabs
    return string

#allows bs4 to parse the required address
def get_soup(address):
    request_link = BASE + address
    re = requests.get(request_link)
    logging.debug("requesting url: " + request_link + " : " + str(re))
    soup  = bs4.BeautifulSoup(re.content, 'lxml')
    return soup

def match_team_names(soup):
    team_names = [name.text for name in soup.find_all(class_="match-item-vs-team-name")]
    return (team_names[0], team_names[1])

#returns scores about live matches 
def get_live_matches():
    matches_soup = get_soup(MATCHES)
    live_matches = matches_soup.find_all(class_="wf-module-item match-item mod-color mod-left mod-bg-after- mod-first")
    live_matches_results = []
    for match in live_matches:
        #if match is not live, there is no point in checking further
        match_status = rm_tabs_newlines(match.find(class_="ml-status").text) 
        if  match_status != "LIVE":
            break
        scores = match.find_all(class_="match-item-vs-team-score")
        single_match = ({"teams" : [rm_tabs_newlines(team) for team in match_team_names(match)] ,
                         "score" : rm_tabs_newlines(scores[0].text) + ":" + rm_tabs_newlines(scores[1].text)} )
        live_matches_results.append(single_match)
    #if the match between the first 2 teams playing is null, it means that no teams are playing at the moment. 
    if (len(live_matches_results) == 0):
        return "No live matches at the moment"
    else:
        return live_matches_results
    

#returns useful information on a match, given the id
#should work, but needs to add check if the matches are actually being played live
def get_match_by_id(id):
    match_soup = get_soup(str(id))
    event = match_soup.find(class_="match-header-event").text
    match_style = rm_tabs_newlines(match_soup.find_all(class_="match-header-vs-note")[1].text)
    date = rm_tabs_newlines(match_soup.find(class_="moment-tz-convert").text)
    total_score = rm_tabs_newlines(match_soup.find(class_="js-spoiler").text)
    teams = [rm_tabs_newlines(result.text) for result in match_soup.find_all(class_="wf-title-med")]
    match_info = {
        "link": BASE + str(id), 
        "id" : id, "event" : rm_tabs_newlines(event), 
        "teams" : teams, "score": total_score, 
        "date" : date,
        "match_style": match_style,
        "players_stats" : team_match_stats(match_soup)
    }
    return match_info

#gets stats from inside a match div
def team_match_stats(soup):
    match_stats = []
    stats_tab = soup.find(class_="vm-stats-container")
    players_hrefs = stats_tab.find_all("a", href=True)
    players_name = stats_tab.find_all(class_="text-of")
    players_kills = stats_tab.find_all(class_="mod-stat mod-vlr-kills")
    players_deaths = stats_tab.find_all(class_="mod-stat mod-vlr-deaths")
    players_assists = stats_tab.find_all(class_="mod-stat mod-vlr-assists")
    players_adrs = stats_tab.find_all(class_="stats-sq mod-combat")
    for i in range(10):
        player_name = rm_tabs_newlines(players_name[i].text)
        kills = rm_tabs_newlines(players_kills[i].text)
        deaths =  rm_tabs_newlines(players_deaths[i].find(class_="stats-sq").text)
        assists = rm_tabs_newlines(players_assists[i].text)
        adr = rm_tabs_newlines(players_adrs[i].text)
        playerstats = {"name" :  player_name.strip(), "link": (players_hrefs[i])['href'],
                       "kills" : int(kills), "deaths": int(deaths.replace("/", "")),
                       "assists": int(assists), "adr" : float(adr)
                       }
        match_stats.append(playerstats)
    return match_stats

#gets information about the top n, with default to global (as a region). Other regions can be specified and passed as a string
def get_top_n(number=30, region=""):
    rankings_soup = get_soup(RANKINGS + region)
    teams = rankings_soup.find_all(class_="rank-item wf-card fc-flex")
    teams_array = []
    for i in range(number):
        team_name = rm_tabs_newlines(teams[i].find(class_="ge-text").text)
        team_country = rm_tabs_newlines(teams[i].find(class_="rank-item-team-country").text)
        team_name = team_name.replace(team_country, "") #removes the country from the team name
        team_ranking = rm_tabs_newlines(teams[i].find(class_="rank-item-rank").text)
        ratings_arr = teams[i].find_all(class_="rank-item-rating")
        streak = rm_tabs_newlines(teams[i].find(class_="rank-item-streak mod-right").text)
        teams_array.append({"team": team_name,
                            "country": team_country,
                            "ranking": int(team_ranking), "rating": int(ratings_arr[0].text),
                            "form": int(ratings_arr[1].text), "ach": int(ratings_arr[2].text),
                            "streak": streak})
    return teams_array 
    #could add winnings and last played, but is functional

#gets basic info about news  such as title, comments and time passed.
def get_news(page=1):
    news_soup = get_soup(NEWS+ f"?page={page}")
    news_list = news_soup.find_all(class_="wf-module-item", href=True) 
    news_array = []
    for article in news_list:
        divs = article.find_all("div")
        title = rm_tabs_newlines(divs[1].text)
        description = rm_tabs_newlines(divs[2].text)
        bot_row = (article.find_next(class_="ge-text-light").text).split("\u2022") # splits the string using the escape for the bullet (u+2022) 
        news_array.append({"title": title, "description" : description, "link": article['href'],
                           "author" : rm_tabs_newlines(bot_row[2]), "date" : bot_row[1]})
    return news_array

def get_player_stats(id):
    player_soup = get_soup(PLAYER +  str(id))
    header = player_soup.find(class_="wf-card mod-header mod-full") 
    name = header.find(class_="wf-title").text
    real_name = header.find(class_="player-real-name").text
    twitter_link =  header.find("a", href=True)
    twitch_link =  header.find_next("a", href=True)
    country = header.find_all("div")
    player_stats = {"name": rm_tabs_newlines(name), "real_name" : real_name, 
                    "twitter" : twitter_link["href"], "twitch" : twitch_link["href"], 
                    "country": rm_tabs_newlines(country[6].text)}
    player_matches_soup = get_soup(PLAYER + MATCHES + str(id))
    matches_stats  = []
    matches = player_matches_soup.find_all(class_="wf-card", href=True)
    for match in matches:
        divs = match.find_all("div")
        score = rm_tabs_newlines(match.find(class_="m-item-result").text) 
        dateclass = match.find(class_="rm-item-datze")
        date = rm_tabs_newlines(dateclass.find("div").text)
        team1 = rm_tabs_newlines(divs[3].text) 
        team2 = rm_tabs_newlines(divs[10].text)
        matches_stats.append({"link": match["href"],"score" : score, "date" : date, "teams": [team1.split("#")[0] ,team2.split("#")[0]]})
    player_stats["matches"] = matches_stats
    return player_stats 

def to_json(filename ,object, indent=4):
    f = open(f"{filename}.json", "w")
    json_object = json.dumps(object, indent=indent)
    f.write(json_object)
    f.close()

dict = get_news()
to_json("news", dict)