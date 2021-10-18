# thespike-api
Unofficial JSON API for thespike.gg, the most famous competitive Valorant website.
This project aims at making esports fans lives easier by getting all kinds of useful infos that can be found on thespike.gg, without the hurdle of having to download 
and format hundreds of matches. For example, if we wanted to get all the  live matches and their scores, we could simply call the function 
```python 
get_live_matches()
```
, which returns a result like this:
```json
[
    {
        "teams": [
            "Fire Flux Esports",
            "Bonsoir"
        ],
        "score": "0:0"
    },
    {
        "teams": [
            "Team Finest",
            "SAW"
        ],
        "score": "0:0"
    }
]
```
## Functions:
```python
get_live_matches()
get_top_n(n_teams, region) #gets top n teams in the selected region
get_match_by_id(id)
get_news(year, month)
get_forum_posts(category)
```
## This project is stil work in progress, so feel free to suggest ways to make it better or make contribution to the codebase!
