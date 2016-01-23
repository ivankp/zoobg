#!/usr/bin/env python

import sys, requests, getpass

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

with requests.Session() as s:
    page = s.post('http://zooescape.com/login.pl', payload)

    # if page.text.find('Logging in.') != -1:

    print dict(s.cookies)

    page = s.get('http://zooescape.com/backgammon.pl?gid=2966357')

    print page.text

    # else:
    #     print 'ERROR: Cannot log in.'
