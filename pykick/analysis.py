#! /usr/bin/python
# -*- coding:utf-8 -*-


'''
functions to load data obtained by scraper.py into pandas data frames
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

def get_season( filename ):
    '''
    takes a season data afile that was generated with scraper.py
    and returns pandas data from with columns:
    Spieltag, Tag, Datum, Zeit, Heim, Gast, Tore (H), Tore (A), Tore Hz (H),
    Tore Hz (A)
    '''
    df = pd.read_csv( filename, sep='\t', na_values='-', skiprows=1 )
    df.columns = ['Spieltag', 'Tag', 'Datum', 'Zeit', 'Heim', 'Gast', 'Tore (H)', 'Tore (A)',\
                      'Tore Hz (H)', 'Tore Hz (A)']
    return df

def get_table(season, three_points=True):
    if three_points:
        win = 3
    else:
        win = 2
    draw = 1
    clubs1 = list(season[ season['Spieltag'] == 1 ]['Heim'])
    clubs2 = list(season[ season['Spieltag'] == 1 ]['Gast'])
    clubs = clubs1 + clubs2
    season['Punkte (H)'] = season['Tore (H)'] - season['Tore (A)']
    season['Punkte (A)'] = season['Tore (A)'] - season['Tore (H)']
    def assign_points( x ):
        if x > 0: 
            return win
        elif x == 0:
            return draw
        else: 
            return 0
    season['Punkte (H)'] = map(assign_points, season['Punkte (H)'])
    season['Punkte (A)'] = map(assign_points, season['Punkte (A)'])
    table = []
    for club in clubs:
        #print club
        points_H = season[ season['Heim'] == club ]['Punkte (H)'].sum()
        points_A = season[ season['Gast'] == club ]['Punkte (A)'].sum()
        points = points_H + points_A
        tore_H = season[ season['Heim'] == club ]['Tore (H)'].sum()
        tore_A = season[ season['Gast'] == club ]['Tore (A)'].sum()
        tore = tore_H + tore_A
        gtore_H = season[ season['Heim'] == club ]['Tore (A)'].sum()
        gtore_A = season[ season['Gast'] == club ]['Tore (H)'].sum()
        gtore = gtore_H + gtore_A
        siege_H = len(season[ (season['Heim'] == club) & (season['Punkte (H)'] == win) ].index)
        niederlagen_H = len(season[ (season['Heim'] == club) & (season['Punkte (H)'] == 0) ].index)
        draw_H = len(season[ (season['Heim'] == club) & (season['Punkte (H)'] == 1) ].index)
        siege_A = len(season[ (season['Gast'] == club) & (season['Punkte (A)'] == win) ].index)
        niederlagen_A = len(season[ (season['Gast'] == club) & (season['Punkte (A)'] == 0) ].index)
        draw_A = len(season[ (season['Gast'] == club) & (season['Punkte (A)'] == 1) ].index)
        siege = siege_H + siege_A
        niederlagen = niederlagen_H + niederlagen_A
        draws = draw_H + draw_A
        table.append( [club, points, tore, gtore, siege, draws, niederlagen, tore_H, tore_A, gtore_H, gtore_A, points_H, points_A, siege_H, draw_H, niederlagen_H, siege_A, draw_A, niederlagen_A] )

    df = pd.DataFrame( table )
    df.columns = ['Verein', 'Punkte', 'Tore', 'Gegentore', 'Siege', 'Unentschieden', 'Niederlagen', 'Tore (H)', 'Tore (A)', 'Gegentore (H)', 'Gegntore (A)', 'Punkte (H)', 'Punkte (A)', 'Siege (H)', 'Untentschieden (H)', 'Niederlagen (H)', 'Siege (A)', 'Unentschieden (A)', 'Niederlagen (A)']
    df.sort( 'Punkte', ascending=False, inplace=True)
    df.index = range(1, len(df.index)+1)
    return df


def player_season( filename ):
    '''
    takes a player data file that was genreated with scraper.py
    return pandas data frame with columns:
    'H/A', 'Gegner', 'Ergebnis', 'Note', 'Tore', 'Elfm', 'Ass',
    'Scp', 'Eing', 'Ausg', 'Rot', 'GelbRot', 'Gelb', 'Punkte'
    '''

    with open(filename , 'r') as f:
        season, name, position, club, birthday, height, weight, nation, competition, i = _read_file_header(f)
    names = ['SpT', 'H/A', 'Gegner', 'Ergebnis', 'Note', 'Tore', 'Elfm',\
                'Ass', 'Scp', 'Eing', 'Ausg', 'Rot', 'GelbRot',  'Gelb']
    df = pd.read_csv( filename, sep='\t', skiprows=i, names=names, index_col=False, na_values='-' )
    #print season
    df.season = season
    df.name = name
    df.position = position
    df.club = club
    df.birthday = birthday
    df.height = height
    df.weight = weight
    df.nation = nation
    df.competition = competition
    df.set_index( 'SpT', inplace=True )
    #print position
    punkte = []
    for i, row in df.iterrows():
        tore = row['Tore']
        note = row['Note']
        rot = row['Rot']
        gelb_rot = row['GelbRot']
        ass = row['Ass']
        if not np.isnan(row['Note']) and np.isnan(row['Eing']):
            von_beginn = True
        else:
            von_beginn = False
        if not np.isnan(row['Eing']):
            eingewechselt = True
        else:
            eingewechselt = False
        ergebnis = row['Ergebnis']
        #print name
        #print season
        #print ergebnis
        ergebnis = ergebnis.strip( 'n.V.\xc2\xa0')
        ergebnis = ergebnis.strip( 'i. E.\xc2\xa0')
        #print ergebnis
        pos = ergebnis.find(':')
        tore_heim = int(ergebnis[:pos])
        tore_gast = int(ergebnis[pos+1:pos+2])
        if row['H/A'] == 'H' and tore_gast == 0:
            zu_null = True
        elif row['H/A'] == 'A' and tore_heim == 0:
            zu_null = True
        else:
            zu_null = False
        #print note, tore, rot, gelb_rot, ass, von_beginn, eingewechselt, zu_null
        p = _calc_manager_interactive_points(position, note, tore, rot, gelb_rot,\
                                             ass, von_beginn, eingewechselt,\
                                             zu_null)
        punkte.append(p)
    df['Punkte'] = punkte
    return df


def player_total( filename_prefix, path ):
    '''
    filename_prefix: name and id of player. Example: 'philipp-lahm_id-26870'
    path: path to player data files
    returns pandas data frame with season as index and columns:
    'Note', 'Tore', 'Ass', 'Scp', 'Rot', 'GelbRot', 'Gelb', 'Punkte',
    'Einsaetze', 'Spielminuten'
    '''
    files = subprocess.check_output( 'ls '+path+filename_prefix+'*', shell=True )
    files = files.split()
    index = []
    data = []
    for f in files:
        df = player_season( f )
        if df.competition == '1. Bundesliga':
            index.append( df.season[:4] )

            durchgespielt = (len(df.index) - df['Ausg'].count() - df['Eing'].count()) * 90
            eingewechselt = df['Eing'].count() * 90-df['Eing'].sum()
            ausgewechselt = df['Ausg'].sum()

            spielminuten = durchgespielt
            if not np.isnan(eingewechselt): spielminuten = spielminuten + eingewechselt
            if not np.isnan(ausgewechselt): spielminuten = spielminuten + ausgewechselt

            data.append( [df['Note'].mean(), df['Tore'].sum(), df['Ass'].sum(), \
                              df['Scp'].sum(), df['Rot'].sum(), df['GelbRot'].sum(), \
                              df['Gelb'].sum(), df['Punkte'].sum(), len(df.index), \
                              spielminuten] )
    if len( data ) == 0:
        return None
    columns =  ['Note', 'Tore', 'Ass', 'Scp', 'Rot', 'GelbRot', 'Gelb', \
                            'Punkte', 'Einsaetze', 'Spielminuten']
    index = pd.to_datetime( index )
    #print index
    player_df = pd.DataFrame( data, index=index, columns=columns )
    #pd.to_datetime( df.index )
    player_df.name = df.name 
    return player_df
    

def players_database( filename ):
    '''
    reads the players.dat file created by scraper.make_players_database()
    into a pandas data frame and returns the data frame.
    columns: 'Nachname', 'Vorname', 'id', 'Position', 'Nummer', 'Verein',
    'Geburtstag', 'Groesse', 'Gewicht', 'Nation', 'prefix'
    '''
    df = pd.read_csv( filename, sep='\t' )
    cols = []
    for c in df.columns:
        cols.append(c.strip('# '))
    df.columns = cols
    df['Geburtstag'] = pd.to_datetime(df['Geburtstag'], format='%d.%m.%Y')
    return df


####################################################################
# Plotting #########################################################
####################################################################
def data_disclaimer( axes, position, source='www.kicker.de', color='grey' ):
    axes.annotate( 'Daten von '+source, xy=position, \
                       xycoords='axes fraction', fontsize=10, color=color),

####################################################################
# Helper functions #################################################
####################################################################

def _calc_manager_interactive_points(position, note, tore, rot, gelb_rot, ass,\
                                       von_beginn, eingewechselt, zu_null ):
    if not np.isnan(note):
        grade_points = -4 * note + 14
    else:
        grade_points = 0.
    if not np.isnan(rot) or not np.isnan(gelb_rot):
        card_points = -6
    elif not np.isnan(gelb_rot):
        card_points = -3
    else:
        card_points = 0.
    if not np.isnan(ass):
        ass_points = ass
    else:
        ass_points = 0.
    if von_beginn:
        start_points = 2
    elif eingewechselt:
        start_points = 1
    else:
        start_points = 0.

    if position == 'Torwart':
        if not np.isnan(tore):
            goal_points = tore * 6
        else:
            goal_points = 0.
        if zu_null:
            zero_game_points = 2
        else:
            zero_game_points = 0.
    if position == 'Abwehr':
        if not np.isnan(tore):
            goal_points = tore * 5
        else:
            goal_points = 0.
        zero_game_points = 0.
    if position == 'Mittelfeld':
        if not np.isnan(tore):
            goal_points = tore * 4
        else:
            goal_points = 0.
        zero_game_points = 0.
    if position == 'Sturm':
        if not np.isnan(tore):
            goal_points = tore * 3
        else:
            goal_points = 0.
        zero_game_points = 0.
    #print grade_points, card_points, ass_points, start_points, goal_points, zero_game_points
    score = grade_points + card_points + ass_points + \
        start_points + goal_points + zero_game_points
    return score


def _read_file_header(file_instance):
    
    def read_line(line, startswith, done ):
        if line.startswith( startswith ):
            pos1 = line.find(':') + 2
            pos2 = line.find('\n')
            attr = line[pos1:pos2]
            return attr, True
        else:
            return None, False

    i = 0

    found_season = False
    found_surname = False
    found_name = False
    found_position = False
    found_height = False
    found_weight = False
    found_nation = False
    found_birthday = False
    found_competition = False
    

    read_club = False
    for line in file_instance:
        i = i + 1
        if not found_season: season, found_season = read_line( line, '# Season', found_season )
        if not found_surname: surname, found_surname = read_line( line, '# Vorname', found_surname )
        if not found_name: name, found_name = read_line( line, '# Nachname', found_name )
        if not found_position: position, found_position = read_line( line, '# Position', found_position )
        if not found_height: height, found_height = read_line( line, '# Gr', found_height )
        if not found_weight: weight, found_weight = read_line( line, '# Gewicht', found_weight )
        if not found_nation: nation, found_nation = read_line( line, '# Nation', found_nation )
        if not found_birthday: birthday, found_birthday = read_line( line, '# Geboren', found_birthday )
        if not found_competition: competition, found_competition = read_line( line, '# Competition', found_competition )
        if read_club:
            pos = line.find('\n')
            club = line[2:pos]
            read_club = False
        if line.startswith( '# Aktueller Verein'):
            read_club = True
        if line.startswith( '#SpT' ):
            break
    name = surname+' '+name
    return season, name, position, club, birthday, height, weight, nation, competition, i
    
###########################################################
# Helper functions ########################################
###########################################################

def get_season_string(year):
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



if __name__ == '__main__':
    pass
    
