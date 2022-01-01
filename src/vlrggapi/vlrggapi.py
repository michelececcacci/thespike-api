from json import encoder
import bs4
import logging
import json
import requests
from requests.api import request
from datetime import date, datetime
import typing



logging.basicConfig(level=logging.DEBUG)

BASE: str = "https://www.vlr.gg/"
MATCHES: str = "matches/"
RANKINGS: str= "rankings/"
NEWS: str = "news/"
FORUMS: str = "forum/"
PLAYER: str = "player/"

class RequestString(str):
    def __init__(self, string: str) -> None:
        self.string = string

    def remove_newlines(self):
        self.string = self.string.replace("\n", "")
        return self

    def remove_tabs(self):
        self.string = self.string.replace("\t", "")
        return self

    def __repr__(self) -> str:
        return self.string
    

#allows bs4 to parse the required address
def get_soup(address :str):
    request_link: str = BASE + address
    re = requests.get(request_link)
    logging.debug("requesting url: " + request_link + " : " + str(re))
    soup  = bs4.BeautifulSoup(re.content, 'lxml')
    if re.status_code == 404:
        return None
    else:
        return soup

def match_team_names(soup)-> tuple:
    team_names = [name.text for name in soup.find_all(class_="match-item-vs-team-name")] 
    return (team_names[0], team_names[1])

#returns scores about live or past matches 
def get_matches_by_status(status: str):
    matches_soup = get_soup(MATCHES)
    live_matches = matches_soup.find_all(class_="wf-module-item") 
    matches_by_status = []
    for match in live_matches:
        #checks if there is any match with the corresponding status
        match_status = RequestString(match.find(class_="ml-status").text) 
        match_status.remove_newlines().remove_tabs()
        if  match_status.lower() != status:
            pass
        else:
            scores = match.find_all(class_="match-item-vs-team-score")
            series = RequestString(match.find(class_="match-item-event-series").text)
            tournament_name = RequestString((match.find(class_="match-item-event").text).replace(series, ""))
            series.remove_tabs().remove_newlines()
            single_match = {"teams" : [RequestString(team).remove_newlines().remove_tabs() for team in match_team_names(match)], 
                            "time" :  RequestString(match.find(class_="match-item-time").text).remove_newlines().remove_tabs(),
                            # grabs info about the tournament, 
                            "series" : series,
                            #since there is no way to get the tournament directly, first it grabs tournament and series, then removes the series
                            "tournament": tournament_name.remove_tabs().remove_newlines()
                            } 
            if (status == "live"):
                single_match["score"] = RequestString(scores[0].text).remove_newlines().remove_tabs() 
                + ":" + RequestString(scores[1].text).remove_newlines().remove_tabs()
            matches_by_status.append(single_match)
    if (len(matches_by_status) == 0):
        return f"No {status} matches at the moment"
    else:
        return matches_by_status
    

#returns useful information on a match, given the id
#should work, but needs to add check if the matches are actually being played live
def get_match_by_id(id: int)-> dict:
    match_soup = get_soup(str(id))
    event = match_soup.find(class_="match-header-event").text
    match_style = RequestString(match_soup.find_all(class_="match-header-vs-note")[1].text)
    match_style.remove_newlines()
    match_style.remove_tabs()
    date = RequestString(match_soup.find(class_="moment-tz-convert").text)
    date.remove_newlines() 
    date.remove_tabs() 
    total_score = RequestString(match_soup.find(class_="js-spoiler").text)
    total_score.remove_tabs() 
    total_score.remove_newlines() 
    teams = [RequestString(result.text).remove_newlines() for result in match_soup.find_all(class_="wf-title-med")]
    match_info: dict = {
        "link": BASE + str(id), 
        "id" : id, "event" : RequestString(event).remove_newlines(), 
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
        player_name = RequestString(players_name[i].text).remove_newlines().remove_tabs()
        kills = RequestString(players_kills[i].text).remove_newlines().remove_tabs()
        deaths =  RequestString(players_deaths[i].find(class_="stats-sq").text).remove_newlines()
        assists = RequestString(players_assists[i].text).remove_newlines().remove_tabs()
        adr = RequestString(players_adrs[i].text).remove_tabs().remove_tabs()
        playerstats = {"name" :  player_name.strip(), "link": (players_hrefs[i])['href'],
                       "kills" : int(kills),  "deaths": int(deaths.replace("/", "")),
                       "assists": int(assists), "adr" : float(adr)
                       }
        match_stats.append(playerstats)
    return match_stats

#gets information about the top n, with default to global (as a region). Other regions can be specified and passed as a string
def get_top_n(number: int=30, region: str=""):
    rankings_soup = get_soup(RANKINGS + region)
    teams = rankings_soup.find_all(class_="rank-item wf-card fc-flex")
    teams_array = []
    for i in range(number):
        team_name = RequestString(teams[i].find(class_="ge-text").text).remove_newlines().remove_tabs().string
        team_country = RequestString(teams[i].find(class_="rank-item-team-country").text).remove_tabs().remove_newlines()
        team_name = team_name.replace(team_country, "") #removes the country from the team name
        team_ranking = RequestString(teams[i].find(class_="rank-item-rank").text).remove_tabs().remove_newlines().string
        ratings_arr = teams[i].find_all(class_="rank-item-rating")
        streak = RequestString(teams[i].find(class_="rank-item-streak mod-right").text).remove_newlines().remove_tabs()
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
        title = RequestString(divs[1].text).remove_newlines().remove_tabs()
        description = RequestString(divs[2].text).remove_newlines().remove_tabs()
        bot_row = (article.find_next(class_="ge-text-light").text).split("\u2022") # splits the string using the escape for the bullet (u+2022) 
        news_array.append({"title": title, "description" : description, "link": article['href'],
                           "author" : RequestString(bot_row[2]).remove_tabs().remove_newlines(), "date" : bot_row[1]})
    return news_array

#gets player infos from personal page
def get_player_infos(id: int)->dict:
    player_soup = get_soup(PLAYER +  str(id))
    header = player_soup.find(class_="wf-card mod-header mod-full") 
    name = header.find(class_="wf-title").text
    real_name = header.find(class_="player-real-name").text
    twitter_link =  header.find("a", href=True)
    twitch_link =  header.find_next("a", href=True)
    country = header.find_all("div")
    return  {"name": RequestString(name).remove_newlines().remove_tabs(), "real_name" : real_name, 
                    "twitter" : twitter_link["href"], "twitch" : twitch_link["href"], 
                    "country": RequestString(country[6].text).remove_tabs().remove_newlines()}

#returns array of last 50 matches played by player given the id
def get_player_matches_by_id(id: int):
    player_matches_soup = get_soup(PLAYER + MATCHES + str(id))
    matches_stats  = []
    matches = player_matches_soup.find_all(class_="wf-card", href=True)
    for match in matches:
        divs = match.find_all("div")
        score = RequestString(match.find(class_="m-item-result").text).remove_newlines().remove_tabs()
        dateclass = match.find(class_="rm-item-datze")
        date = RequestString(dateclass.find("div").text).remove_tabs().remove_newlines()
        team1 = RequestString(divs[3].text).remove_tabs().remove_newlines()
        team2 = RequestString(divs[10].text).remove_tabs().remove_newlines
        matches_stats.append({"link": match["href"],"score" : score, "date" : date, "teams": [team1.split("#")[0] ,team2.split("#")[0]]})
    return matches_stats
    
def to_json(filename: str , object: dict, indent=4):
    f = open(f"{filename}.json", "w")
    json_object = json.dumps(object, indent=indent)
    f.write(json_object)
    f.close()
