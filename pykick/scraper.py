#! /usr/bin/env python

'''
Functions for web scraping of www.kicker.de
'''

import mechanize # provides the browser class for web scraping
from bs4 import BeautifulSoup # analysis tools for html files
import datetime
import warnings
import timeit
import subprocess


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
    season_str = _get_season_string( year )
    clubs_url = 'http://www.kicker.de/news/fussball/bundesliga/vereine/1-bundesliga/'+season_str+'/vereine-liste.html'
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

def get_player_statistics(path):
    '''
    get player information and statistics of all current Bundesliga players for
    all available seasons
    path: path to the directory where the data will be saved
    creates one file per player and season with name 
    "${vorname}-${nachname}_id-${id}_${season}"
    data columns: SpT, H/A, Gegner, Ergebnis, Note, Elfm, Ass, ScP, Eing,
    Ausg, Rot, GelbRot, Gelb
    '''

    start = timeit.default_timer()
    print 'Extracting player statistics from www.kicker.de'
    print 'Saving data in '+path
    counter = 1
    base_url = 'www.kicker.de'
    year = datetime.date.today().year
    season_str = _get_season_string( year )
    browser = start_browser() # open browser
    clubs_url = 'http://www.kicker.de/news/fussball/bundesliga/vereine/1-bundesliga/'+season_str+'/vereine-liste.html' # address with table of clubs
    content = browser.open( clubs_url ) # open URL
    soup = BeautifulSoup(content) # load html file in BeautifuleSoup object
    club_table = soup.find('table') # get the table of clubs
    for link in club_table.find_all('a'): # loop through all the links in the table
        #print link.text
        if link.text == 'Kader': # get the links to the player table
            kader_link = link.get('href') # the link
            #print kader_link
            content = browser.open( kader_link ) # open link in browser
            soup = BeautifulSoup( content ) # put html in BeautifulSoup object
            for player_link in soup.find_all('a'): # loop throug all the links to the player information
                plink = player_link.get('href') # get URL
                #print plink
                if plink: # for some reason there is a None type sometimes
                    if plink.find('/spieler_') != -1: # thats a link to player inf
                        output = 'Get statistics for player no. '+str(counter)
                        #print '\r{0}'.format( output )+'',
                        print output
                        counter = counter + 1
                        pos1 = plink.find( '/spieler_' ) - 5
                        pos2 = plink.find( '/spieler_' )
                        player_id = plink[pos1:pos2] # get spieler id
                        pos1 = plink.find('/spieler_' ) + 9
                        pos2 = plink.find('.html')
                        name = plink[pos1:pos2]
                        #print name
                        #print player_id
                        content = browser.open( plink ) # open URL in browser
                        soup = BeautifulSoup( content ) # construct BeautifulSoup object
                        seasons_list = soup.find('dl') # get list of available seasons
                        for season_link in seasons_list.find_all('a'): # loop through seasons
                            slink = season_link.get('href') # get URL
                            content = browser.open( slink ) # open URL in browser
                            soup = BeautifulSoup( content ) # put html in BeautifulSoup object
                            season_str = season_link.text.replace('/', '-') # thats the season
                            info = soup.find('table', {'class':'infoBox'}) # player information
                            info = info.text
                            info = info.replace(':\n', ': ')
                            info = info.replace('\n\n\n', '\n')
                            info = info.replace('\n\n', '\n')
                            info = info.replace('\n', '\n# ')

                            #print info.text

                            # extract the competition the statistics is for
                            competition_table = soup.find('table', {'class':'tStat tStatKarten'} )
                            rows = competition_table.find_all('tr')
                            cols = rows[1].find_all('td')
                            competition = cols[0].text

                            # extract statistics
                            stat = soup.find('table', {'class':'tStat noBackground'}) # player statistics
                            rows = stat.find_all('tr')
                            filename = name+'_id-'+player_id+'_'+season_str
                            with open( path+filename, 'w+') as f:
                                output = '# Season: '+season_str+'\n'
                                f.write( output )
                                f.write( '\n' )
                                f.write( '#'*60+'\n' )
                                f.write( '# Player information '+'#'*39+'\n' )
                                f.write( '#'*60+'\n' )
                                f.write( info.encode('utf-8') )
                                f.write( '\n' )
                                f.write( '#'*60 )
                                f.write( '\n\n\n' )
                                f.write( '# Competition: '+competition.encode('utf-8')+'\n')
                                output = '#SpT\t#H/A\t#Gegner\t#Ergebnis\t#Note\t#Tore\t#Elfm\t#Ass\t#Scp\t#Eing\t#Ausg\t#Rot\t#GelbRot\t#Gelb\n'
                                for r in rows[1:]:
                                    line = ''
                                    columns = r.find_all('td')
                                    if len(columns) == 14:
                                        for c in columns:
                                            text = c.text.strip('\n')+'\t'
                                            if text == '\t':
                                                text = '-\t'
                                            line += text
                                        line = line.replace('&nbsp;', ' ')
                                        line = line.replace(',', '.')
                                        output += line
                                        #print line
                                        output += '\n'
                                #print output
                                f.write( output.encode('utf-8') )
    stop = timeit.default_timer()
    print 'Saved statistics for '+str(counter)+' players in '+str(stop-start)+' seconds.'

def make_players_database(path):

    files = subprocess.check_output( 'ls '+path+' | grep -v dat | grep -v py' , shell=True )
    files = files.split()

    ids = []
    names = []
    surnames = []
    prefixes = []
    positions = []
    numbers = []
    clubs = []
    birthdays = []
    heights = []
    weights = []
    nations = []

    for filename in files:
        pos = filename.find( '_' ) + 4
        id_no = filename[pos:pos+5]
        prefix = filename[:pos+5]
        with open(filename, 'r') as f:
            get_club = False
            for line in f.readlines():
                if line.startswith( '# Vorname:' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find( '\n' )
                    vorname = line[pos1:pos2]

                if line.startswith( '# Nachname:' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    nachname = line[pos1:pos2]

                if line.startswith( '# Position:' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    position = line[pos1:pos2]

                if line.startswith( '# Geboren am:' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    birthday = line[pos1:pos2]

                if line.startswith( '# Gr' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    height = line[pos1:pos2]

                if line.startswith( '# Gewicht' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    weight = line[pos1:pos2]

                if line.startswith( '# Nation:' ):
                    pos1 = line.find(':') + 4
                    pos2 = line.find('\n')
                    nation = line[pos1:pos2]

                if line.startswith( '# R' ):
                    pos1 = line.find(':') + 2
                    pos2 = line.find('\n')
                    number = line[pos1:pos2]

                if get_club:
                    pos = line.find('\n')
                    club = line[2:pos]
                    get_club = False

                if line.startswith( '# Aktueller Verein:' ):
                    get_club = True


        if id_no not in ids:
            ids.append( id_no )
            names.append( nachname )
            surnames.append( vorname )
            prefixes.append( prefix )
            positions.append( position )
            numbers.append( number )
            clubs.append( club )
            birthdays.append( birthday )
            heights.append( height )
            weights.append( weight )
            nations.append( nation )

    playerlist = zip( names, surnames, ids, positions, numbers,\
                          clubs, birthdays, heights, weights, \
                          nations, prefixes )
    playerlist.sort()

    with open( 'players.dat', 'w+') as f:
        f.write( '# Nachname\t# Vorname\t# id\t# Position\t# Nummer\t# Verein\t# Geburtstag\t# Groesse\t# Gewicht\t# Nation\t# prefix\n' )
        for player in playerlist:
            for i in player:
                print i
            f.write( player[0]+'\t'+player[1]+'\t'+player[2]+'\t'+player[3]+'\t'\
                         +player[4]+'\t'+player[5]+'\t'+player[6]+'\t'+player[7]+'\t'\
                         +player[8]+'\t'+player[9]+'\t'+player[10]+'\n' )


###########################################################
# Helper functions ########################################
###########################################################

def _get_season_string(year):
    '''
    Example: year=2014 -> return '2014-15'
    '''
    year_p1 = str(year%100+1)
    if len(year_p1) == 1: # prepend a 0
        year_p1 = '0' + year_p1
    if len(year_p1) == 3: # get rid of the 1
        year_p1 = year_p1[1:]
    assert len(year_p1) == 2 # make sure that we have a proper date string
    return str(year)+'-'+year_p1
    



