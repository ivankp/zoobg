#!/usr/bin/env python

from bitarray import bitarray

#state = 'b2G5I3m5N5r3t5Y2'
#state = 'C2D3F2u1w1x1zCA8'
state = 'z8ACC1D1F1u2w3x2'
print state

bit_array = bitarray()
for a in 'BCDEFGHIJKLMNOPQRSTUVWXYZyxwvutsrqponmlkjihgfedcba':
    #print a
    i = state.find(a)
    if i!=-1:
        while i%2==1:
            i = state.find(a,i+1)
            if i==-1: break
        if i!=-1:
            for j in range(int(state[i+1],16)):
                bit_array.append(True)
    bit_array.append(False)
while len(bit_array)<80: bit_array.append(False)

print bit_array

bit_array2 = bitarray()
for i in range(10):
    for j in reversed(range(8)):
        bit_array2.append(bit_array[i*8:i*8+8][j])
    # print bit_array[i*8:i*8+8]
    # print bit_array2[i*8:i*8+8]
while len(bit_array2)<14*6: bit_array2.append(False)

base64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
s = ""
for byte in range(14):
    i = 0
    for bit in range(6):
        i = (i << 1) | bit_array2[byte*6+bit]
    s += base64[i]

print 'set board %s' % (s)
