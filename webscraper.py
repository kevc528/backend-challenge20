from bs4 import BeautifulSoup
from models import *
import requests

def get_content(url):
    res = requests.get(url)
    return res.content

def get_clubs(soup):
    return soup.findAll('div', {'class': 'box'})

def get_club_name(club):
    elts = club.findAll('strong', {'class': 'club-name'})
    if len(elts) < 1:
        return ''
    return elts[0].text

def get_club_description(club):
    return club.em.text

def get_club_tags(club):
    elts = club.findAll('span', {'class': 'tag'})
    return list(map(lambda x: x.text, elts))

def scrape_clubs():
    url = 'https://ocwp.pennlabs.org'
    html = get_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    clubs_html = get_clubs(soup)
    json_clubs = []
    for club_html in clubs_html:
        name = get_club_name(club_html)
        description = get_club_description(club_html)
        tags = get_club_tags(club_html)
        code = "".join(word[0] for word in name.split())
        club_obj = {
            'code': code,
            'name': name,
            'description': description,
            'tags': tags
        }
        json_clubs.append(club_obj)
    return json_clubs