#!/usr/bin/env python

import sys, re, requests, getpass

def find_all_between( s, first, last ):
    blocks = []
    start = 0
    while True:
        start = s.find( first, start )
        if start == -1:
            return blocks
        start += len( first )
        end = s.find( last, start )
        if end == -1:
            return blocks
        blocks.append( s[start:end] )

def pickup_from_ladder(s, n):
    ladder = s.get('http://zooescape.com/ladder.pl?l=1').text
    games  = find_all_between(ladder,
        'game-start-special','>Challenge</A></TD></TR>')

    ladder = s.get( 'http://zooescape.com' + find_all_between(ladder,
            '<table class="page_menu"><tr><td><a href="',
            '" title="previous page">')[0]
        ).text
    games  = find_all_between(ladder,
        'game-start-special','>Challenge</A></TD></TR>') + games

    for i in range(min(n,len(games))):
        print games[i]
        form = find_all_between( s.get(
                    'http://zooescape.com/game-start-special' + \
                games[i].strip('\"')).text, '<FORM', '</FORM>' )
        if len(form)>0:
            action = 'http://zooescape.com' + find_all_between(
                form[0][:form[0].find('>')],'action=\"','\"' )[0]

            values = dict( val for sublist in \
                [ re.findall(r'name=\"([^\"]+)\" +(?:value=\"?([^\"]+)\"?)',x) \
                  for x in find_all_between(form[0],'<INPUT','>') ] \
                  for val in sublist )

            print action
            print values

            s.post(action, values)

        else: break

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

with requests.Session() as s:
    pw_attempts = 0
    while s.post('http://zooescape.com/login.pl', payload
                ).text.find('Logging in.') == -1:
        pw_attempts += 1
        if pw_attempts > 2: sys.exit(1)
        else: payload['password'] = getpass.getpass()

    pickup_from_ladder(s,1)
