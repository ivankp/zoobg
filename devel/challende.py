#!/usr/bin/env python

import sys, requests

from fab import find_all_between
from zelogin  import login
from zeladder import ladder

with requests.Session() as s:
    cred = { 'userName': raw_input('Username: ') \
                         if len(sys.argv)<2 else sys.argv[1],
             'password': None }
    login(s, cred)

    print s.post('http://zooescape.com/game-start-special.pl?v=200', {
        'game_start_challenge_submit': '1',
        'opp': sys.argv[2],
        'ttm': '3',
        'l': '1' } ).text

