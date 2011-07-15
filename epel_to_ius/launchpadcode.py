from urllib2 import urlopen
from re import compile

def repos():
    '''return a list of repos from the Launchpad Code page'''
    u = urlopen('https://code.launchpad.net/ius')
    page = u.read()
    repos = compile('bazaar.launchpad.net/~ius-coredev/ius/(.*)/revision/\d').findall(u)
    return repos
