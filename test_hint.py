#!/usr/bin/env python

from zehint import hint

alphA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphz = 'zyxwvutsrqponmlkjihgfedcba'

def test(h):
    print "Hits : ", h.hits
    print "Moves: ", h.moves
    print ''.join([str(x) for x in h.dice])+''.join([ \
          (alphA if True else alphz)[x[0]] \
          for x in h.moves ])
    print ""


# GNU Backgammon  Position ID: tu0UAiAWAAAAAA
#                 Match ID   : cIkGAAAAAAAA
#test(hint( "3/off", [1,5], [1] ))

# GNU Backgammon  Position ID: zwcBAPjdIwAAAA
#                 Match ID   : cIkKAAAAAAAA
#test(hint( "6/off", [5,2], [] ))

#test(hint( "6/off", [2,2], [] ))

#test(hint( "5/off 4/2", [6,2], [] ))

test(hint( "1/off", [5,4], [] ))
