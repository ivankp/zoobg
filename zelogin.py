import sys, getpass
from logfile import logfile

def get_pass_interruptible(cred):
    try:
        cred['password'] = getpass.getpass()
    except (KeyboardInterrupt):
        print ''
        sys.exit(1)


def login(s, cred, attempts=1, logfile=None):
    # s: requests.Session
    # cred: map; login credentials
    # attempts: int; max num
    # log: str or None; log file name
    if cred['password'] is None:
        get_pass_interruptible(cred)
    pw_attempts = 0
    while s.post('http://zooescape.com/login.pl',cred).\
            text.find('Logging in.') == -1:
        pw_attempts += 1
        if pw_attempts == attempts:
            print 'Cannot login as %s with this password' % (cred['userName'])
            sys.exit(1)
        else:
            get_pass_interruptible(cred)
    if logfile is not None:
        logfile.write('logged in as %s' % (cred['userName']))
    print 'Login success'
