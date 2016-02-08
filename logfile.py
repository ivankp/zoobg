import datetime

class logfile:
    def __init__(self,fname):
        self.fname = fname
    def write(s):
        with open(self.fname,'a') as f:
            f.write(datetime.datetime.now().\
              strftime("%Y-%m-%d %H:%M:%S")+' '+s+'\n')
