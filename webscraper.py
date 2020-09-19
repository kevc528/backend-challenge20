from bs4 import BeautifulSoup
from models import *
import requests

def get_content(url):
    """
    Fetch html content from a given url
    """
    res = requests.get(url)
    return res.content

def get_clubs(soup):
    """
    Get HTML of clubs from soup
    """
    return soup.findAll('div', {'class': 'box'})

def get_club_name(club):
    """
    Get club name from club html
    """
    elts = club.findAll('strong', {'class': 'club-name'})
    if len(elts) < 1:
        return ''
    return elts[0].text

def get_club_description(club):
    """
    Get club description from club html
    """
    return club.em.text

def get_club_tags(club):
    """
    Get club tags from club html
    """
    elts = club.findAll('span', {'class': 'tag'})
    return list(map(lambda x: x.text, elts))

def scrape_clubs():
    """
    Scrape the clubs from the site and return a list of json 
    """
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