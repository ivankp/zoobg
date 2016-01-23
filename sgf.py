#!/usr/bin/env python

def other(player):
    return 'W' if player=='B' else 'B'

match = '34NY21mt46ZN42rt4414tb24ZK62bf5531mp32ZY61mq53XS26ao64IG41ar53PN62mm62WQ52af55OJGG1246KK4262WQ31au64OI34rs46NJ56ah33ZGII1543WS3164PJ3444EEEG1256GG1151FB2323DD2542FC52a14Z43aa15YX63nr21SQ44hluu24Z55dins21ZX52ae51WR44pttf41QM21jl5466gmmh34Z44ssfj2151ns4325np6132tu6652uu6141vw3451tt3244vvuw44ZVRN42wx41JB36ww12BC16yx44FCBB36xy46B'

print '''\
(;FF[4]GM[6]CA[UTF-8]AP[zooescape.com]\
MI[length:1][game:0][ws:0][bs:0]\
PW[%s]PB[%s]\
DT[%s]\
''' % ('white','black','2016-01-09')

moves = []
for c in match:
    if c == '#': # cube
        moves.append('#')
    elif c.isdigit(): # dice
        if len(moves)==0:
            moves.append(c)
        elif len(moves[-1])>=2:
            if moves[-1][-1].isalpha() or (moves[-1][-1].isdigit() and moves[-1][-2].isdigit()):
                moves.append(c)
            else:
                moves[-1] += c
        else:
            moves[-1] += c
    else: # moves
        moves[-1] += c

sgf_pos_b =      'yabcdefghijklmnopqrstuvwxz'
dictb = dict(zip('ZYXWVUTSRQPONMLKJIHGFEDCBA', sgf_pos_b))
sgf_pos_w =      'zabcdefghijklmnopqrstuvwxy'
dictw = dict(zip('zyxwvutsrqponmlkjihgfedcba', sgf_pos_w))

player = 'B' if moves[0][-1].islower() else 'W' # needs to be backward
for m in moves:
    player = other(player)
    if m[0] == '#':
        print ';%s[double]' % (player)
        if len(m)>1:
            print ';%s[take]' % (other(player))
            m = m[1:]
    move = ';%s[%s' % (player,m[0:2])

    for i in range(2,len(m)):
        if player=='W':
            move += dictw[m[i]]
            move += sgf_pos_w[max(sgf_pos_w.find(move[-1])-int(m[i%2]),0)]
        else:
            move += dictb[m[i]]
            move += sgf_pos_b[min(sgf_pos_b.find(move[-1])+int(m[i%2]),25)]

    move += ']'
    print move

print ')'
