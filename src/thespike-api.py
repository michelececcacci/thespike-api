import bs4
import json
import requests
from requests.api import request
from datetime import date, datetime


BASE = "https://www.thespike.gg/"
MATCHES = "matches/"
MATCH = "match/"
RANKINGS = "rankings/"
NEWS = "news/"
NEWS_ARCHIVE = "news/archive/"
FORUMS = "forums/general-discussion/"

months_strings = {1: "january", 2 : "february", 3: "march", 
                4 : "may", 5: "april", 6: "june", 7 : "july", 
                8: "august", 9: "september", 10 : "october",
                 11 : "november" , 12: "december"}

def remove_spaces(string):
    string = string.replace(" ", "") #eliminates whitespaces 
    string = string.replace("\n", "") #eliminates newlines 
    return string

#allows bs4 to parse the required address
def get_soup(address):
    request_link = BASE + address
    re = requests.get(request_link)
    print("requesting url: " + request_link + " : " + str(re))
    soup  = bs4.BeautifulSoup(re.content, 'lxml')
    return soup

def match_team_names(soup):
    team_names = [name.text for name in soup.find_all(class_="team-name")]
    return (team_names[0], team_names[1])

#returns scores about live matches
def get_live_matches():
    matches_soup = get_soup(MATCHES)
    live_section = matches_soup.find(id="live-matches-sidebar-module")
    single_matches = live_section.find_all(class_="single-match element-trim-button")
    live_matches_results = []
    for match in single_matches:
        scores = match.find_all(class_="scores")
        single_match = ({"teams" : match_team_names(match) , "score" : remove_spaces(scores[0].text) + ":" + remove_spaces(scores[1].text)} )
        live_matches_results.append(single_match)
    return live_matches_results
    

#returns useful information on a match, given the id
def get_match_by_id(id):
    match_soup = get_soup(MATCH + str(id))
    banner = match_soup.find(class_="match-single_top-banner main-area-default element-trim-normal")
    event = match_soup.find(class_="event-details").text
    total_score = match_soup.find(class_="match-score number").text
    total_score = remove_spaces(total_score)
    team_1_pred = match_soup.find(class_="team-one-percentage percentage-display").text
    team_2_pred = match_soup.find(class_="team-two-percentage percentage-display").text
    team1_stats_unparsed = match_soup.find(id="allMapsTotalTeamOne")
    team2_stats_unparsed = match_soup.find(id="allMapsTotalTeamTwo")
    team1_stats = team_match_stats(team1_stats_unparsed)
    team2_stats = team_match_stats(team2_stats_unparsed)
    match_info = {
        "link": BASE + MATCH + str(id), 
        "id" : id, "event" : event.strip(), 
        "teams" : match_team_names(banner), "score": total_score, 
        "preds" :[team_1_pred, team_2_pred], 
        "team1Stats": team1_stats, "team2Stats" : team2_stats
    }
    return match_info

def team_match_stats(soup):
    team_stats = []
    player_names = soup.find_all(class_="single-stat tablestat-f4")
    # player_ratings = soup.find_all(class_="single-stat main-area-alt tablestat-f1 number") # todo this doesn't work because all the various stats have all the same class
    player_kdas = soup.find_all(class_="single-stat main-area-alt tablestat-f3 number")
    for i in range(len(player_names)):
        kda = remove_spaces(player_kdas[i].text)
        kda_list = kda.split('|')
        playerstats = {"playerName" : player_names[i].text, "kills": kda_list[0],"deaths": kda_list[1], "assists" : kda_list[2]} 
        team_stats.append(playerstats)
    return team_stats

#gets information about the top n, with default to global (as a region). Other regions can be specified and passed as a string
def get_top_n(number=30, region=""):
    rankings_soup = get_soup(RANKINGS + region)
    teams = rankings_soup.find_all(class_="single-team-ranking main-colour-background")
    teams_array = []
    for i in range(number):
        team_name = remove_spaces(teams[i].find(class_="team-name").text)
        team_ranking = remove_spaces(teams[i].find(class_="ranking-position number").text)
        team_roster = remove_spaces(teams[i].find(class_="team-roster").text)
        ranking_points = remove_spaces(teams[i].find(class_="points").text)
        form_points = remove_spaces(teams[i].find(class_="form").text)
        achv_points = remove_spaces(teams[i].find(class_="achievements").text)
        teams_array.append({"team": team_name, "ranking": int(team_ranking), "roster": team_roster, "points" : int(ranking_points), "form": int(form_points), "achv" :  int(achv_points)})
    return teams_array 

#gets basic info about news  such as title, comments and time passed
def get_news(year=datetime.now().year, month=datetime.now().month):
    news_soup = get_soup(NEWS_ARCHIVE + f"{year}/{months_strings[month]}")
    news_list = news_soup.find_all(class_="item element-trim-button")
    news_array = []
    for news in news_list:
        title = (news.find(class_="news-title").text).strip()
        comments  = news.find(class_="comments").text
        date = news.find(class_="date").text
        link = news.find("a", href=True)
        news_array.append({"title": title, "date" : date,"comments":comments, "link": BASE + NEWS + link['href']})
    return news_array

# parses  forum posts
def get_forum_posts(category):
    forum_soup = get_soup(FORUMS + str(category))
    posts = forum_soup.find_all(class_="item main-colour-background element-trim-button")
    posts_array = []
    for post in posts:
        author = remove_spaces(post.find(class_="username").text)
        title = (post.find(class_="forum-title").text).strip()
        date = (post.find(class_="date").text).strip()
        posts_array.append({"title": title, "author" : author, "date": date})
    return posts_array
    

def to_json(filename ,object, indent=4):
    f = open(f"{filename}.json", "w")
    json_object = json.dumps(object, indent=indent)
    f.write(json_object)
    f.close()
