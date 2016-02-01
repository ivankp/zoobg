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

    html = s.get('http://zooescape.com/backgammon-room.pl').text

    table = find_all_between(find_all_between(html,'RoomObjInit','RoomSetup')[0],'[',']')

    head = find_all_between( table[0], 'title:StringDecodeJS(\'', '\')' )

    si = head.index('Game%3cBR%3eStatus') # status index
    ti = head.index('Game%3cBR%3eType')   # type index
    
    print si
    print ti

    for row in [ find_all_between(x,'{','}') for x in table[2:] ]:
      if row[si].find('My Turn')!=-1:
          i = row[si].find('gid=')+4
          gid = row[si][i:i+7]
