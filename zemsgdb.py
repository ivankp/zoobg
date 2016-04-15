import urllib, sqlite3
from fab import find_all_between

class zemsg:
    def __init__(self,txt):
        for field in [ x.split(':') for x in txt.split(',')]:
            if field[0]=='mID':
                self.mid = int(field[1])
            elif field[0]=='mTime':
                self.time = int(field[1])
            elif field[0]=='mNumID':
                self.who = field[1]
            elif field[0]=='mText':
                self.msg = urllib.unquote(field[1][16:-2])
    def __str__(self):
        return str(self.mid)+' from '+self.who \
               +' at '+str(self.time)+':\n'+'  '+self.msg

def check_msgs(filename,page,gid,opp):
    msglist = find_all_between(page,'MessageList([{','}])')
    if len(msglist)!=1: return

    db = sqlite3.connect(filename)
    cur = db.cursor()

    new_msgs = False
    for msg in [ zemsg(x) for x in msglist[0].split('},{') ]:
        cur.execute('SELECT mid FROM zemsgs WHERE mid = ?', (msg.mid,))
        if cur.fetchone() is None: # Message is new
            cur.execute('INSERT INTO zemsgs VALUES (?,?,?,?,?)',
                (msg.mid,gid,opp,msg.time,msg.msg,) )
            new_msgs = True
            print msg

    if new_msgs: db.commit()
