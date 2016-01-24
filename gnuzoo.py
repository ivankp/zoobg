#!/usr/bin/env python

# References:
# https://www.gnu.org/software/gnubg/manual/gnubg.html#A-technical-description-of-the-Position-ID

import sys, requests, re, getpass
from bitarray import bitarray
from subprocess import Popen, PIPE, STDOUT

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

alphA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphz = 'zyxwvutsrqponmlkjihgfedcba'

def get_pip( board, caps ):
    pip = 0
    k = 0
    for a in alphA if caps else alphz:
        i = board.find(a)
        if i!=-1:
            while i%2==1:
                i = board.find(a,i+1)
                if i==-1: break
            if i!=-1:
                pip += k*int(board[i+1],16)
        k += 1
    return pip

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
base64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def encode_idbits(bit_array):
    bit_array2 = bitarray()
    for i in range(len(bit_array)/8):
        for j in reversed(range(8)):
            bit_array2.append(bit_array[i*8:i*8+8][j])

    while len(bit_array2)%6 != 0: bit_array2.append(False)

    gnubgid = ""
    for byte in range(len(bit_array2)/6):
        i = 0
        for bit in range(6):
            i = (i << 1) | bit_array2[byte*6+bit]
        gnubgid += base64[i]

    return gnubgid

class game:
    def __init__(self,board,match,state,players):
        self.board = board
        self.match = match
        self.state = state
        self.p0 = players[0]
        self.p1 = players[1]

    def white(self):
        return self.p0 if self.p0[5]=='a' else self.p1

    def black(self):
        return self.p0 if self.p0[5]=='A' else self.p1

def read_board(game_page):
    # Get game state variables ######################################
    GameSetupMP = find_all_between( game_page, 'Backgammon.GameSetupMP(', ');' )[0]
    SetStateMP  = find_all_between( game_page, 'Backgammon.SetStateMP(', ');' )[0]

    players = [ [ y.strip('\'') for y in x.strip(' ').split(', ') ]
                for x in find_all_between( GameSetupMP, 'new PlayerBG(', ')' ) ]

    setup_tail = GameSetupMP[GameSetupMP.rfind(']')+3:].split(', ')

    state = [ x.strip(' "') for x in SetStateMP.split(', ') ]

    moving = (0 if players[0][0] == state[2] else 1)

    logcube = int(state[6])
    if logcube>0: logcube -= 1

    # Flip board if necessary #######################################
    if players[moving][5] == 'A':
        # Moving player is black => switch white and black
        num = len(state[0])/2
        for i in reversed(range(num)):
            state[0] += (
                alphabet[ len(alphabet) - alphabet.find( state[0][i*2] ) - 1 ]
            )
            state[0] += state[0][i*2+1]
        state[0] = state[0][num*2:]

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

    board = encode_idbits(bit_array)

    # Encode GNU Backgammon match ID ################################
    cube_owner = str(players[moving][11] + players[1 if moving==0 else 0][11])
    if cube_owner[0]!='1':
        cube_owner = '00' if cube_owner[1]!='1' else '11'

    bit_array = bitarray(72)
    bit_array.setall(False)
    bit_array[0:4] = bitarray(
        bin(logcube)[:1:-1].ljust(4,'0') ) # cube value
    bit_array[4:6] = bitarray(cube_owner) # cube owner
    bit_array[6:7] = bitarray('1') # dice owner
    bit_array[7:8] = bitarray('0') # Crawford
    bit_array[8:11] = bitarray('100') # game sate
    bit_array[11:12] = bitarray([players[1][0]==state[2]]) # turn owner
    bit_array[12:13] = bitarray('0') # double
    bit_array[13:15] = bitarray('00') # resignation
    bit_array[15:18] = bitarray(
        bin(int(state[3][0]))[:1:-1].ljust(3,'0') ) # die 1
    bit_array[18:21] = bitarray(
        bin(int(state[3][1]))[:1:-1].ljust(3,'0') ) # die 2
    bit_array[21:36] = bitarray('100000000000000') # match length
    #bit_array[36:51] = bitarray('010000000000000') # score 1
    #bit_array[51:66] = bitarray('001000000000000') # score 2

    match = encode_idbits(bit_array)

    return game(board,match,state,players)

def int_move(move):
    ab = move.split('/')
    if ab[0]=='bar': ab[0]='25'
    if ab[1]=='off': ab[1]='0'
    ab = [ int(x) for x in ab ]
    return ab

#####################################################################
# Open requests session #############################################
with requests.Session() as s:
    # Log in --------------------------------------------------------
    login_page = s.post('http://zooescape.com/login.pl', {
        'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
        'password': getpass.getpass()
    }).text
    if login_page.find('Logging in.') == -1:
        print login_page
        sys.exit(1)

    # Read game page ------------------------------------------------
    gid = '2971431'
    url = 'http://zooescape.com/backgammon.pl?v=200&gid=%s' % (gid)
    g = read_board(s.get(url).text)
    print g.board+':'+g.match+'\n'

    # Get hint from gnubg -------------------------------------------
    pipe = Popen(['/usr/games/gnubg','-t'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    gnubg = pipe.communicate( input='''
set sound enable false
set threads 4
set evaluation chequerplay evaluation plies 3
set evaluation cubedecision evaluation cubeful off

set beavers 0
set jacoby off

new game
set matchid %s
set board %s
hint
''' % (g.match,g.board) )[0]

    gnubg = gnubg[gnubg.rfind(' GNU Backgammon'):]
    if len(gnubg)==0:
        print 'GNU Backgammon failed unexpectedly'
        sys.exit(1)
    print gnubg
    gnubg = gnubg[gnubg.rfind('    1. '):]
    gnubg = gnubg[:gnubg.find('Eq')]
    gnubg = gnubg[gnubg.rfind('ply')+3:].strip()

    # gnubg = '5/off 6/2'

    moves = [ int_move(x) for x in re.findall(r'[^ ]+/[^ ]+', gnubg) ]
    print moves
    moves = sorted(moves, key=lambda x: x[0]-x[1])
    print moves
    moves = ''.join([ (alphA if g.black()==g.p1 else alphz)[x[0]]
                      for x in moves ])
    print moves

    # Send move request ---------------------------------------------
    move = {
        'bg_form_moves'   : ''.join(sorted(list(g.state[3])))+moves,
        'bg_form_pips_b'  : str(get_pip(g.state[0],g.black()==g.p1)),
        'bg_form_pips_w'  : str(get_pip(g.state[0],g.white()==g.p1) \
                            - int(g.state[3][0]) - int(g.state[3][1]) ),
        'bg_submit'       : '1',
        'bg_button_submit': 'Submit',
        'bg_turn_num'     : len(re.findall(r'[1-6]{2}[a-zA-Z]+', g.state[1]))
    }
    print move
