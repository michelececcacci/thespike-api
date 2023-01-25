# thespike-api
Unofficial JSON API for the valorant website vlr.gg 

## installation:
clone the repo  and install the package locally with respectively: 
```
git clone git@github.com:michelececcacci/thespike-api.git
cd thespike-api
sudo python3 -m pip install ./
```
Then, you can simply import the package anywhere with 
```python3 
from thespikeapi import thespikeapi
```
## Available functions
* [`get_matches_by_status`](#matches-by-status)
* [`get_match_by_id()`](#match-by-id)
* [`get_top_n()`](#get-top-n)
* [`get_news()`](#get-news)

#### Matches by status
request:
```python
get_matches_by_status("live")
```
Response: 
```json
[
    {
        "teams": [
            "Gamelanders Purple",
            "Try eSports"
        ],
        "time": "9:00 PM",
        "series": "Main Event\u2013Upper Quarterfinals",
        "tournament": "Protocolo: Evolu\u00e7\u00e3o",
        "score": "0:0"
    }
]
```
#### Match by id
Takes the id of the wanted match, and retrieves info about it. Here showing only one player for brevity

request: 
```python
get_match_by_id(43000)
```
```json
{
    "link": "https://www.vlr.gg/43000",
    "id": 43000,
    "event": "LVP Rising Series #4Playoffs: Semifinals",
    "teams": [
        "Giants Gaming",
        "TENSTAR"
    ],
    "score": "0:2",
    "date": "Thursday, October 21st",
    "match_style": "Bo3",
    "players_stats": [
        {
            "name": "hoody",
            "link": "/player/2690/hoody",
            "kills": 16,
            "deaths": 14,
            "assists": 5,
            "adr": 123.2
        },
        {
            "name": "Fit1nho",
            "link": "/player/292/fit1nho",
            "kills": 16,
            "deaths": 15,
            "assists": 3,
            "adr": 104.9
        }
    ]
```
#### Get top n
request
```python
get_top_n(region="europe")
```
```json
[
    {
        "team": "Gambit Esports",
        "country": "Russia",
        "ranking": 1,
        "rating": 2499,
        "form": 1999,
        "ach": 500,
        "streak": "4W"
    },
    {
        "team": "Team Liquid",
        "country": "Europe",
        "ranking": 2,
        "rating": 2319,
        "form": 2000,
        "ach": 319,
        "streak": "4W"
    }
]
```

#### Get news
request:
```python
get_news()
```
Response: 
```json
[
    {
        "title": "Alliance, CLG Red, Gamelanders - News Almost Missed October 22",
        "description": "This week's edition of News Almost Missed comes with a healthy scoop of stories from around the world.",
        "link": "/47125/alliance-clg-red-gamelanders-news-almost-missed-october-22",
        "author": " by Hudsen",
        "date": " October 23, 2021 "
    }
]

```
### This project is still work in progress, so feel free to suggest ways to make it better or make contribution to the codebase!
