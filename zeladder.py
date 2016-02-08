from fab import find_all_between

class ladder:
    def __init__(self,html):
        lines = find_all_between(html,
                '<TH>Finished</TH><TH>&nbsp;</TH></TR>\n',
                '</TABLE>')[0].rstrip('\n').split('\n')
        self.challenges = []
        self.own_rank = 0
        for l in lines:
            if l[-23:][:-14]=='Challenge':
                self.challenges.append( (
                    int( find_all_between(l,'>','<')[1] ),
                    find_all_between(l,'game-start-special','\">')[0] ) )
            elif l[-23:][:-14]=='lected_li': # own line
                self.own_rank = int( find_all_between(l,'>','<')[1] )

    def above(self,above):
        if above: return [ x for x in self.challenges if x[0]<self.own_rank ]
        else: return self.challenges
