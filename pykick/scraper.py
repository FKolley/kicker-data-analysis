#! /usr/bin/env python

'''
Functions for web scraping of www.kicker.de
'''

import mechanize # provides the browser class for web scraping
from bs4 import BeautifulSoup # analysis tools for html files
import datetime
import warnings


def start_browser():
    '''
    Initializes a mechanize.Browser instance and sets options
    needed to scrape www.kicker.de
    Returns the Browser
    '''
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', ('Mozilla/4.0'))] # pretend you are not a robot
    return browser

def kicker_login(username, password):
    '''
    starts a mechanize browser and logs in at www.kicker.de
    Returns the loged in browser
    '''
    login_url = 'https://secure.kicker.de/community/login'
    browser = start_browser()
    browser.open( login_url )
    browser.select_form( nr=2 ) # thats where the login form is.
    browser.form['nickname'] = username
    browser.form['password'] = password
    browser.submit()
    return browser

def get_club_list( year=datetime.date.today().year ):
    '''
    Returns the list of clubs that played in the Bundesliga
    in the season year/year+1. Earliest season is 1963.
    '''
    club_list = []
    year_p1 = str(year%100+1)
    if len(year_p1) == 1: # prepend a 0
        year_p1 = '0' + year_p1
    if len(year_p1) == 3: # get rid of the 1
        year_p1 = year_p1[1:]
    assert len(year_p1) == 2 # make sure that we have a proper date string
    clubs_url = 'http://www.kicker.de/news/fussball/bundesliga/vereine/1-bundesliga/'+str(year)+'-'+year_p1+'/vereine-liste.html'
    browser = start_browser() # start browser
    content = browser.open( clubs_url ) # open url in browser
    soup = BeautifulSoup( content ) # load content of url in BeautifulSoup object
    club_table = soup.find('table') # get the table of clubs
    rows = club_table.findAll('tr') # get the rows of the table
    for r in rows[1::2]: # loop through the rows and extract the club name
        column = r.find('td') # get 1st column. There is the club name
        club_list.append( column.text.strip('\n') ) # append club name to the list
    if len(club_list) == 0:
        warnings.warn('No clubs found. get_club_list() returned an empty list. Used URL: '+clubs_url)
    return club_list


    


if __name__ == '__main__':
    clubs = get_club_list(year=2000)
    print clubs
