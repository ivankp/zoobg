#!/usr/bin/env python

import sys, requests, getpass

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

r1 = requests.post('http://zooescape.com/login.pl', payload)

print dict(r1.cookies)

r2 = requests.post('http://zooescape.com/backgammon.pl?gid=2966357',
    # cookies=r1.cookies
    cookies={'SESSIONID': 'c19cJoajDSwkmoQUw73fa', 'LOGIN': '1', 'PLTN': '1453257601_29690', 'ZEO': '~0101000~~004'}
    )

print r2.text
print r2.text.find('Log Out')
