#!/usr/bin/env python

import sys, requests, re, getpass

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('user', nargs='?', help='zooescape username')
parser.add_argument('-g','--gid','--game', nargs='*',
    help='save only these games')
parser.add_argument('--last',
    help='gid of the last game to save')
parser.add_argument('-p','--player', nargs='?',
    help='get this user\'s games')
args = parser.parse_args()

from fab import find_all_between
from zelogin import login

#####################################################################
# Open requests session #############################################
with requests.Session() as s:
    cred = { 'userName': raw_input('Username: ') \
                         if args.user is None else args.user,
             'password': None }
    login(s, cred, 3)

    url = 'http://zooescape.com/game-list.pl?usr=%s&type=p' % (
        args.player if args.player is not None else cred['userName'])

    all_rows = ''

    while True:
        print url
        page = s.get(url).text

        all_rows += find_all_between(page,'\n],[\n','\n\n],')[0]
        all_rows += '\n,\n'

        b = page.rfind('title=\"next page\"')
        if b==-1: break
        else:
            url = 'http://zooescape.com'+page[page[0:b].rfind('href=\"')+6:b-2]

    file1 = open("gameslist.txt", 'w')
    file1.write(all_rows)
    file1.close()

    for url in [ find_all_between(x,'href=\"','\">')[0] for x in all_rows.split('\n,\n') if len(x)>0 ]:
        print url
        file2 = open(find_all_between(url,'gid=','&')[0]+'.html', 'w')
        file2.write( s.get('http://zooescape.com'+url).text )
        file2.close()


