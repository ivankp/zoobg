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

class msgdb:
    def __init__(self,filename):
        self.db = sqlite3.connect(filename)
        self.cur = self.db.cursor()

    def check(self,page,gid):
        new_msgs = False
        for msg in [ zemsg(x) for x in \
            find_all_between(page,'MessageList([{','}])')[0].split('},{')
        ]:
            self.cur.execute('SELECT mid FROM zemsgs WHERE mid = ?', (msg.mid,))
            if self.cur.fetchone() is None: # Message is new
                self.cur.execute('INSERT INTO zemsgs VALUES (?,?,?,?,?)',
                    (msg.mid,gid,msg.who,msg.time,msg.msg,) )
                new_msgs = True
                print msg

        if new_msgs: self.db.commit()
