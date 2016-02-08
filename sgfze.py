#!/usr/bin/env python

import sys, requests, re, getpass

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('user', nargs='?', help='zooescape username')
parser.add_argument('-g','--gid','--game', nargs='*',
    help='save only these games')
parser.add_argument('--last',
    help='gid of the last game to save')
args = parser.parse_args()
