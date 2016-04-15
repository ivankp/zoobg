#!/usr/bin/env python

import sys, requests, re, getpass

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('user', nargs='?', help='zooescape username')
parser.add_argument('-g','--gid','--game')
parser.add_argument('--sqldb', help='sql database file for messages')
args = parser.parse_args()

from fab import find_all_between
from zelogin import login
from zemsgdb import msgdb

#####################################################################
# Open requests session #############################################
with requests.Session() as s:
    cred = { 'userName': raw_input('Username: ') \
                         if args.user is None else args.user,
             'password': None }
    login(s, cred, 3)

    url = 'http://zooescape.com/backgammon.pl?gid=' + args.gid
    page = s.get(url).text

    db = msgdb(args.sqldb)
    db.check(page,args.gid)
