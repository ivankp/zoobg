#!/usr/bin/env python

import sys, re, requests, getpass

payload = {
    'userName': raw_input('Username: ') if len(sys.argv)==1 else sys.argv[1],
    'password': getpass.getpass()
}

def parse(pat, text):
    m = pat.match(text)
    if m != None: return m.group(1)
    else: return ''

def get_rank(text,usr):
    txt = text.split('\n')
    txt = [x for x in txt if x.find(usr)!=-1][0]
    txt = txt[:txt.find('</TD>')]
    return int(txt[txt.rfind('>')+1:])

class game:
    usr_i  = -1
    gid_i  = -1
    pip_i  = -1
    type_i = -1
    time_i = -1

    td_re   = re.compile(r'\{[^\{\}]*\}+')
    usr_re  = re.compile(r'\{t:PlayerLink\(\'(.*)\',.*\).*')
    gid_re  = re.compile(r'.*A href=\".*gid=(\d*)\".*')
    pip_re  = re.compile(r'\{t:(.*)\}')
    type_re = re.compile(r'\{t:\'(.*)\'.*')
    time_re = re.compile(r'\{t:\'(.*)\'.*')

    @classmethod
    def read_header(cls, head):
        for i, td in enumerate(cls.td_re.findall(head)):
            if   td.find(r'%3cBR%3eOpponent'     )!=-1: cls. usr_i = i;
            elif td.find(r'Game%3cBR%3eStatus'   )!=-1: cls. gid_i = i;
            elif td.find(r'Pip%3cBR%3eDifference')!=-1: cls. pip_i = i;
            elif td.find(r'Game%3cBR%3eType'     )!=-1: cls.type_i = i;
            elif td.find(r'Time%3cBR%3eLeft'     )!=-1: cls.time_i = i;

    def __init__(self, tr):
        tds = self.td_re.findall(tr)
        self.usr  = parse(self. usr_re, tds[self. usr_i]) if self. usr_i!=-1 else ''
        self.gid  = parse(self. gid_re, tds[self. gid_i]) if self. gid_i!=-1 else ''
        self.pip  = parse(self. pip_re, tds[self. pip_i]) if self. pip_i!=-1 else ''
        self.type = parse(self.type_re, tds[self.type_i]) if self.type_i!=-1 else ''
        self.time = parse(self.time_re, tds[self.time_i]) if self.time_i!=-1 else ''
        self.rank = -1

    def __str__(self):
        return "%15s %7s %4s %1s %8s %4d" % (
            self.usr, self.gid, self.pip, self.type, self.time, self.rank
        )

with requests.Session() as s:
    pw_attempts = 0
    while s.post('http://zooescape.com/login.pl', payload
                ).text.find('Logging in.') == -1:
        pw_attempts += 1
        if pw_attempts > 2: sys.exit(1)
        else: payload['password'] = getpass.getpass()

    table = s.get('http://zooescape.com/backgammon-room.pl').text

    table = table[table.find('Game.mSingleton.mActiveGamesTable'):]
    table = table[:table.find('Game.mSingleton.mActiveGamesTable.Render();')]

    game.read_header(table[table.find('[')+1:table.find(']')])

    games = []

    for tr in table[table.find('[[')+1:table.find(']]')+1].split('\n'):
        games.append(game(tr))

    ladder = [g for g in games if g.type=='L']

    for g in ladder:
        # print g.usr
        g.rank = get_rank(
            s.get('http://zooescape.com/ladder.pl?l=1&usr='+g.usr).text, g.usr)

    ladder = sorted(ladder, key=lambda game: game.rank)

    my_rank = get_rank(
        s.get('http://zooescape.com/ladder.pl?l=1').text, payload['userName'])

    printed_my = False
    for g in ladder:
        if not printed_my and (g.rank > my_rank):
            print "%15s %28d" % (payload['userName'], my_rank)
            printed_my = True
        print g,
        print "%4d" % (g.rank - my_rank)
