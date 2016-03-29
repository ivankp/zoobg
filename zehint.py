import re

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

            pp = [ pos_int[i:i+2] for i in range(0,len(pos_int)-1) ]

            if len(pp)==1 and pp[0][1]==0: # split bearoff moves
                d = pp[0][0]-pp[0][1]
                if d<=self.dice[0]+self.dice[1] \
                and not (d==self.dice[0] or d==self.dice[1]):
                    if self.dice[0] > self.dice[1]:
                        self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
                    p = pp[0][0]-self.dice[0]
                    if p not in points:
                        self.moves = [[pp[0][0],p],[p,0]]
                    else:
                        p = pp[0][0]-self.dice[1]
                        self.moves = [[pp[0][0],p],[p,0]]
                        self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
                    pp = [] # do not loop over pp below

            for p in pp:
                d = p[0]-p[1]
                while d!=self.dice[0] and d!=self.dice[1]:
                    # bear off with larger die
                    if (d<max(self.dice)) and (p[1]==0): break
                    die = self.dice[0]
                    if p[0]-die in points:
                        die = self.dice[1]
                    self.moves.append([p[0],p[0]-die])
                    p[0] = p[0]-die
                    d = p[0]-p[1]
                self.moves.append(p)

        # flip the moves order if necessary
        if len(self.moves)==2:
            if (self.moves[0][0]-self.moves[0][1]>self.dice[0]) \
            or (self.moves[1][0]-self.moves[1][1]>self.dice[1]):
                self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
        elif len(self.moves)==1:
            d = self.moves[0][0]-self.moves[0][1]
            if self.moves[0][1]==0: # single bareoff move
                if d>self.dice[0]: # first die too small
                    self.dice[0], self.dice[1] = self.dice[1], self.dice[0]
            else:
                if d!=self.dice[0]:
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
