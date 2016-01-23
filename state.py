#!/usr/bin/env python

import sys, requests, getpass
from bitarray import bitarray

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

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
base64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

with requests.Session() as s:
    # Read HTML page ################################################
    pw_attempts = 0
    while s.post('http://zooescape.com/login.pl', payload
                ).text.find('Logging in.') == -1:
        pw_attempts += 1
        if pw_attempts > 2: sys.exit(1)
        else: payload['password'] = getpass.getpass()

    gid = raw_input('gid: ') if len(sys.argv)<3 else sys.argv[2]
    page = s.get('http://zooescape.com/backgammon.pl?gid='+gid).text

    # Get game state variables ######################################
    GameSetupMP = find_all_between( page, 'Backgammon.GameSetupMP(', ');' )[0]
    SetStateMP  = find_all_between( page, 'Backgammon.SetStateMP(', ');' )[0]

    players = [ [ y.strip('\'') for y in x.strip(' ').split(', ') ]
                for x in find_all_between( GameSetupMP, 'new PlayerBG(', ')' ) ]

    state = [ x.strip(' "') for x in SetStateMP.split(',')[:2] ]

    # Flip board if necessary #######################################
    is_white = False

    if players[0][1] == payload['userName']:
        if players[0][5] == 'a': is_white = True

    elif players[1][1] == payload['userName']:
        if players[1][5] == 'a': is_white = True

    else:
        print "Player %s is not playing game %s" % (payload['userName'],gid)
        sys.exit(1)

    if is_white==False:
        # Logged in player is black => switch white and black
        num = len(state[0])/2
        for i in reversed(range(num)):
            state[0] += (
                alphabet[ len(alphabet) - alphabet.find( state[0][i*2] ) - 1 ]
            )
            state[0] += state[0][i*2+1]
        state[0] = state[0][num*2:]

    # Print ZooEscape stats #########################################
    print ""
    for i in range(2):
        print "%15s (%s, %3sL)" % (
            players[i][1],players[i][7],players[i][10])
    print ""
    print "ZooEscape board: %s" % (state[0])
    print ""

    print players[0]
    print players[1]
    print state

    print ""

    # Encode GNU Backgammon board ID ################################
    bit_array = bitarray()
    for a in 'BCDEFGHIJKLMNOPQRSTUVWXYZyxwvutsrqponmlkjihgfedcba':
        i = state[0].find(a)
        if i!=-1:
            while i%2==1:
                i = state[0].find(a,i+1)
                if i==-1: break
            if i!=-1:
                for j in range(int(state[0][i+1],16)):
                    bit_array.append(True)
        bit_array.append(False)
    while len(bit_array)<80: bit_array.append(False)

    bit_array2 = bitarray()
    for i in range(10):
        for j in reversed(range(8)):
            bit_array2.append(bit_array[i*8:i*8+8][j])
    while len(bit_array2)<14*6: bit_array2.append(False)

    gnubgid = ""
    for byte in range(14):
        i = 0
        for bit in range(6):
            i = (i << 1) | bit_array2[byte*6+bit]
        gnubgid += base64[i]

    print "GNU Backgammon:"
    print "set board %s" % gnubgid

    # Encode GNU Backgammon match ID ################################

    print ""
