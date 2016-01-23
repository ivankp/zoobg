#!/usr/bin/env python

import sys, requests, re

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

def get_pip( board, alph ):
    pip = 0
    k = 0
    for a in alph:
        i = board.find(a)
        if i!=-1:
            while i%2==1:
                i = board.find(a,i+1)
                if i==-1: break
            if i!=-1:
                pip += k*int(board[i+1],16)
        k += 1
    return pip

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

with requests.Session() as s:
    login = s.post('http://zooescape.com/login.pl', payload).text
    if login.find('Logging in.') == -1:
        print login
        sys.exit(1)

    url = 'http://zooescape.com/backgammon.pl?v=200&gid=2979184'

    page = s.get(url).text

    SetStateMP = find_all_between( page, 'Backgammon.SetStateMP(', ');' )[0]
    state = [ x.strip(' "') for x in SetStateMP.split(',')[:4] ]

    print "Board: " + state[0]
    print "Moves: " + state[1]
    print "Dice : " + state[3]

    move = {
        'bg_form_moves'   : state[3]+'GY',
        'bg_form_pips_w'  : str(get_pip(state[0],'zyxwvutsrqponmlkjihgfedcba')),
        'bg_form_pips_b'  : str(get_pip(state[0],'ABCDEFGHIJKLMNOPQRSTUVWXYZ') \
                            - int(state[3][0]) - int(state[3][1]) ),
        'bg_submit'       : '1',
        'bg_button_submit': 'Submit',
        'bg_turn_num'     : len(re.findall(r'[1-6]{2}[a-zA-Z]+', state[1]))
    }

    s.post(url, move)
