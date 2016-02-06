#!/usr/bin/env python

# References:
# https://www.gnu.org/software/gnubg/manual/gnubg.html#A-technical-description-of-the-Position-ID

import sys, requests, re, getpass, time, datetime
from bitarray import bitarray
from subprocess import Popen, PIPE, STDOUT

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('user', nargs='?', help='zooescape username')
parser.add_argument('-g','--gid','--game', nargs='*',
    help='play only this game')
parser.add_argument('-a','--automatic', action='store_true', default=False,
    help='periodically check for moves')
parser.add_argument('-l','--ladder', action='store_true', default=False,
    help='pick up games from the ladder')
parser.add_argument('--accept', action='store_true', default=False,
    help='accept BG & NG challenges, can\'t play AD')
parser.add_argument('--gnubg',
    help='gnubg program full path')
parser.add_argument('--plies', type=int, default=3,
    help='set threads [3]')
parser.add_argument('--threads', type=int, default=4,
    help='set evaluation chequerplay evaluation plies [4]')
parser.add_argument('--log',
    help='write a log file')
args = parser.parse_args()

if args.gnubg is None:
    args.gnubg=Popen(['which','gnubg'], stdout=PIPE).communicate()[0].rstrip('\n')
    if args.gnubg=='':
        print 'gnubg location must be specified with --gnubg'
        sys.exit(1)

def write_log(s):
    if args.log is not None:
        with open(args.log,'a') as f:
            f.write(datetime.datetime.now().\
              strftime("%Y-%m-%d %H:%M:%S")+' '+s+'\n')

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
    def __init__(self,board,match,state,players,moving):
        self.board = board
        self.match = match
        self.state = state
        self.players = players
        self.moving = moving
        self.moving_black = self.players[self.moving][5]=='A'
        self.dice = [ int(x) for x in state[3] ]

    def opp(self):
        return self.players[1 if self.moving==0 else 0]

def read_board(game_page):
    # Get game state variables ######################################
    GameSetupMP = find_all_between(game_page,'Backgammon.GameSetupMP(',');')[0]
    SetStateMP  = find_all_between(game_page,'Backgammon.SetStateMP(', ');')[0]

    players = [ [ y.strip('\'') for y in x.strip(' ').split(', ') ]
                for x in find_all_between(GameSetupMP,'new PlayerBG(',')') ]

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

    return game(board,match,state,players,moving)

class hint:
    def __init__(self,txt,dice,points):
        self.hits = []
        self.moves = []
        self.dice = dice
        # print 'points = ', points
        rep = re.findall(r'\([2-4]\)',txt)
        txt2 = txt
        if len(rep)>0:
            rep = int(rep[0][1])
            txt2 = re.sub('([^ ]+)\\(%d\\)'%(rep), '\\1 '*rep, txt)
        for move in txt2.split():
            pos = move.split('/')
            pos_int = []
            for p in pos:
                if p=='bar':
                    pos_int.append(25)
                elif p=='off':
                    pos_int.append(0)
                elif p[-1]=='*':
                    p_int = int(p[:-1])
                    self.hits.append(p_int)
                    pos_int.append(p_int)
                else:
                    pos_int.append(int(p))
            for p in [ pos_int[i:i+2] for i in range(0,len(pos_int)-1) ]:
                d = p[0]-p[1]
                while d!=dice[0] and d!=dice[1]:
                    # bear off with larger die
                    if (d<max(dice)) and (p[1]==0): break
                    die = dice[0]
                    if p[0]-die in points:
                        die = dice[1]
                    self.moves.append([p[0],p[0]-die])
                    p[0] = p[0]-die
                    d = p[0]-p[1]
                self.moves.append(p)
        # flip the moves order if necessary
        if (len(self.moves)==2):
            if (self.moves[0][0]-self.moves[0][1]>self.dice[0]) \
            or (self.moves[1][0]-self.moves[1][1]>self.dice[1]):
                self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
        elif len(self.moves)==1:
            if self.moves[0][1]==0:
                if self.moves[0][0]-self.moves[0][1]>self.dice[0]:
                    self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
            else:
                if self.moves[0][0]-self.moves[0][1]!=self.dice[0]:
                    self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
        elif len(self.moves)>2:
            i = 0
            while i<len(self.moves)-1:
                if self.moves[i][1]==0 and self.moves[i+1][1]!=0:
                    self.moves = self.moves[:i]+self.moves[i+1:]+[self.moves[i]]
                else: i += 1
            while i>0:
                if self.moves[i][0]==25 and self.moves[i-1][0]!=25:
                    self.moves = [self.moves[i]]+self.moves[:i]+self.moves[i+1:]
                else: i -= 1

def play(s,gid):
    print 'gid = ', gid

    url = 'http://zooescape.com/backgammon.pl?v=200&gid=%s' % (gid)
    html = s.get(url).text

    # check if logged in
    if html.find('Log in to <A href="/">play Backgammon</A>')!=-1:
       return False

    g = read_board(html)
    print g.board+':'+g.match+'\n'

    # Get hint from gnubg -------------------------------------------
    pipe = Popen([args.gnubg,'-t'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    gnubg = pipe.communicate( input='''
set sound enable false
set threads %d
set evaluation chequerplay evaluation plies %d
set evaluation chequerplay evaluation cubeful off
set evaluation cubedecision evaluation cubeful off

set beavers 0
set jacoby off

set player 0 name %s
set player 1 name %s

new game
set matchid %s
set board %s
hint
''' % (args.threads,args.plies, \
       g.opp()[1],g.players[g.moving][1], \
       g.match,g.board) )[0]

    gnubg = gnubg[gnubg.rfind(' GNU Backgammon'):]
    if len(gnubg)==0:
        print 'GNU Backgammon failed unexpectedly'
        sys.exit(1)
    print gnubg
    l1 = gnubg.rfind('    1. ')
    moves = gnubg[l1:gnubg.find('Eq',l1)]
    moves = moves[moves.rfind('ply')+3:].strip()

    h = hint( moves, g.dice,
        [ 25-alphA.find(x[0]) for x in re.findall(r'[A-Z].', g.state[0]) ]
        # if int(x[1],16)>1 removed
        # count even 1 checker as a point here,
        # because gnubg explicitly marks hits
    )
    print "Hits : ", h.hits
    print "Moves: ", h.moves

    moving_dpip  = -sum([ x[0]-x[1] for x in h.moves ])
    oponent_dpip =  sum(h.hits)

    turn = len(re.findall(r'[1-6]{2}[a-zA-Z]*', g.state[1]))

    # TODO: only roll if needed
    # s.post('http://zooescape.com/backgammon-roll.pl', {
    #     'gid': gid, 'turn': turn-1
    # })

    # Send move request ---------------------------------------------
    s.post(url, {
        'bg_form_moves'   : ''.join([str(x) for x in h.dice])+''.join([ \
                            (alphA if g.moving_black else alphz)[x[0]] \
                            for x in h.moves ]),
        'bg_form_pips_b'  : str(get_pip(g.state[0],not g.moving_black) \
                            + (moving_dpip if g.moving_black else oponent_dpip)),
        'bg_form_pips_w'  : str(get_pip(g.state[0],g.moving_black) \
                            + (oponent_dpip if g.moving_black else moving_dpip)),
        'bg_submit'       : '1',
        'bg_button_submit': 'Submit',
        'bg_turn_num'     : turn
    } )

    if args.log is not None:
        l1 += 6
        l2 = gnubg.find('\n',l1)
        l3 = gnubg.find('\n',l2+1)
        write_log( '%7s %15s %4s %3s\n   %s\n   %s' % (
            gid, g.opp()[1], g.opp()[7], g.opp()[10],
            gnubg[l1:l2], gnubg[l2+7:l3-1]
        ) )

    return True

def pickup_from_ladder(s):
    page  = s.get('http://zooescape.com/ladder.pl?l=1').text
    games = find_all_between(page,
        'game-start-special','>Challenge</A></TD></TR>')

    page  = s.get( 'http://zooescape.com' + find_all_between(page,
            '<table class="page_menu"><tr><td><a href="',
            '" title="previous page">')[0]
        ).text
    games = find_all_between(page,
        'game-start-special','>Challenge</A></TD></TR>') + games

    for g in games:
        form = find_all_between( s.get(
                'http://zooescape.com/game-start-special' + \
            g.strip('\"')).text, '<FORM', '</FORM>' )

        if len(form)>0:
            action = 'http://zooescape.com' + find_all_between(
                form[0][:form[0].find('>')],'action=\"','\"' )[0]

            values = dict( val for sublist in \
                [ re.findall(r'name=\"([^\"]+)\" +(?:value=\"?([^\"]+)\"?)',x) \
                  for x in find_all_between(form[0],'<INPUT','>') ] \
                  for val in sublist )

            msg = 'challenged %s in BG ladder' % (values['opp'])
            print msg
            if args.log is not None: write_log(msg)
            s.post(action, values)

        else: break

max_n_games = 1

def play_all(s):
    room = s.get('http://zooescape.com/backgammon-room.pl').text
    table = find_all_between(
        find_all_between(room,'RoomObjInit','RoomSetup')[0], '[',']' )
    if len(table)==0: return 2 # got kicked out
    head = find_all_between( table[0], 'title:StringDecodeJS(\'', '\')' )

    si = head.index('Game%3cBR%3eStatus') # status index
    ti = head.index('Game%3cBR%3eType')   # type index

    games = [ find_all_between(x,'{','}') for x in table[2:] ]

    global max_n_games
    if len(games)>max_n_games:
        max_n_games = len(games)
        print 'Playing %d games' % (max_n_games)
    elif args.ladder:
        # pick up games from the ladder if has room
        if len(games)<max_n_games: pickup_from_ladder(s)

    played = False

    for row in games:
        if row[si].find('My Turn')!=-1:
            i = row[si].find('gid=')+4
            if not play(s,row[si][i:i+7]): return 2 # got kicked out
            played = True
        elif args.accept and row[si].find('New Challenge')!=-1:
            href = find_all_between(row[si],'href=\"','\"')[0]
            game_type = int(re.findall(r'v=20(\d)',href)[0])
            if game_type==0 or game_type==1:
                s.post('http://zooescape.com'+href,
                        {'bg_challenge_radio':'1',
                         'bg_challenge_message':''} )
            # TODO: reject AD games
            # else:
            #     s.post('http://zooescape.com'+href,
            #             {'bg_challenge_radio':'1',
            #              'bg_challenge_message':''} )

    return 1 if played else 0

def login(s, cred, attempts):
    pw_attempts = 0
    while s.post('http://zooescape.com/login.pl',cred).\
    text.find('Logging in.') == -1:
        pw_attempts += 1
        if pw_attempts == attempts:
            print 'Cannot login as %s with this password' % (cred['userName'])
            sys.exit(1)
        else: cred['password'] = getpass.getpass()
    if args.log is not None: write_log('logged in as %s' % (cred['userName']))
    print 'Login success'

delays = [1, 10, 15, 30, 30, 60, 60, 120, 120, 120, 300, 300, 600]

#####################################################################
# Open requests session #############################################
with requests.Session() as s:
    cred = { 'userName': raw_input('Username: ') \
                         if args.user is None else args.user,
             'password': getpass.getpass() }

    login(s, cred, 3)

    if args.gid is None:
        if args.automatic:
            i = 0
            while True:
                x = play_all(s)
                if x==1: i = 0 # moves were made, pay attention
                elif x==2: # got kicked out, login again
                    time.sleep(5)
                    login(s, cred, 1)
                elif i!=len(delays)-1: i += 1 # max delay reached
                print "sleep %d" % (delays[i])
                time.sleep(delays[i])

        else:
            play_all(s)

    else:
        for gid in args.gid: play(s,gid)
