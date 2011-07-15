#!/usr/bin/env python

import os
import argparse
import cPickle
import shutil
from re import match, search
from tempfile import mkdtemp
from urllib2 import urlopen, HTTPError
from config import get_config

from commands import run
from launchpadcode import lp_repos
from emailer import email

def store_message(p, message):
    '''simple throw away function for storing and notifying'''
    pkgs[p].append(message)
    print message
    return


def main():

    # Build my Parser with help for user input
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', '-e', action='store_true',
                dest='email', default=None, help='Send output in email')
    parser.add_argument('--forcegit', '-f', action='store_true',
                dest='forcegit', default=None, help='Wipe away old Git and start with a fresh repo')
    args = parser.parse_args()

    # get our config
    config = get_config()

    # cache the contents of epel, so we can for loop, and seek on it
    u = urlopen(config['baseurl'])
    f = open(os.path.expanduser(config['baseurl_cache']), 'w')
    f.write(u.read())
    f.close()

    # if we have a cache we will link against it
    # this will verify we only process once per version
    if args.forcegit:
        cache = []
    else:
        if os.path.exists(config['cache_file']):
            cache = cPickle.load(open(config['cache_file'], 'r'))
        else:
            cache = []

    # get a list of all repos in launchpad
    repos = lp_repos()

    # a dict to hold all messages, we will use this to email later
    global pkgs
    pkgs = {}

    # read over our file list of package names
    for p in open(os.path.expanduser(config['pkgfile']), 'r').readlines():
        p = p.strip("\n")

        # empty list to hold our messages
        pkgs[p] = []

        content = open(os.path.expanduser(config['baseurl_cache']), 'r')
        for line in content.readlines():

            # regex to find all SRPM matching our package name
            m = match('.*>((%s-[\w.]*-[\w.]*)[\.el6]?\.src.rpm).*' % p, line)
            if m:
                full_p = m.group(1)
                pkg_name = m.group(2)
                pkg_name = pkg_name.replace('.el6', '')

                # if we have this version lets continue to the next package
                if full_p in cache:
                    store_message(p, '%s is in cache no need to go any further' % p)
                    continue

                # currently repos need to be created manually in LP
                # if a repo does not exist we will be forced to skip
                reponame = p
                print '\n== %s ==' % p
                if reponame not in repos:
                    store_message(p, '%s does not exist in launchpad' % reponame)
                    continue

                # create a tmp location for each package
                # this will end up being the git repo
                tmp = mkdtemp()
                store_message(p, 'working out of %s' % tmp)
                os.chdir(tmp) 

                # all check passed thus far, we can not start our bzr shell commands
                # we now need to worry about success and failures for commands.
                proceed = True

                if proceed: 
                    store_message(p, 'pulling bzr repo')
                    rm = 'lp:~ius-coredev/ius/%s' % p.lower()
                    remote = run(['bzr', 'branch', rm])
                    os.chdir(p)
                    if remote.returncode > 0:
                        proceed = False
                        store_message(p, remote.communicate())

                if proceed:
                    # download the SRPM to current directory
                    store_message(p, 'fetching package for %s' %full_p)
                    f = open(full_p, 'w')
                    pkg = urlopen("%s/%s" % (config['baseurl'], full_p))
                    f.write(pkg.read())
                    f.close()

                if proceed:
                    # install the SRPM
                    store_message(p, 'installing %s' % full_p)
                    rpm = run(['rpm', '-i', full_p])
                    if rpm.returncode > 0:
                        proceed = False
                        store_message(p, rpm.communicate())
                    else:
                        # we do not want the SRPM in the Git repo
                        os.remove(full_p)

                if proceed: 
                    store_message(p, 'adding all files to bzr')
                    add = run(['bzr', 'add', '.'])
                    if add.returncode > 0:
                        proceed = False
                        store_message(p, add.communicate())

                if proceed: 
                    store_message(p, 'commmiting changes to git')
                    commit = run(['bzr', 'commit', '-m', '[commit] %s' % full_p])
                    if commit.returncode > 0:
                        proceed = False
                        store_message(p, commit.communicate())
                
                if proceed: 
                    store_message(p, 'pushing changes to git')
                    if args.forcegit:
                        push = run(['git', 'push', '-f', 'origin', 'master'])
                    else:
                        push = run(['git', 'push', 'origin', 'master'])
                    if push.returncode > 0:
                        proceed = False
                        store_message(p, push.communicate())

                if proceed:
                    # if everything was successful we can add to our cache
                    cache.append(full_p)

                    # save all our work to the pickle cache
                    f = open(os.path.expanduser(config['cache_file']), 'wb')
                    cPickle.dump(cache, f)
                    f.close()

                # at this point the package source is in our repo
                # we can now start to work with Monkey Farm to get
                # a build submitted
                
                if proceed:
                    # lets first verify a package by this name exists in MF
                    from mymonkeyfarm import connect, createpackagebranch, createpackage, createbuild
                    hub = connect()

                    try:
                        hub.package.get_one(p, 'rpmdev')
                    except HTTPError:
                        # It does not appear a package exists, we should create it now
                        spec = open('SPECS/%s.spec' % p, 'r').read()

                        try:
                            summary = search('Summary:(.*)', spec)
                            summary = summary.group(1).lstrip()
                        except AttributeError:
                            store_message(p, 'failed to pull summary from spec')
                            proceed = False
                        else:
                            # We were able to grab the summary
                            # lets start by creating our package
                            store_message(p, 'creating package %s in MF' % p)
                            package = createpackage(hub, p, config['user_label'], summary)
                            for errors in package['errors']:
                                store_message(p, errors + ': ' + package['errors'][errors])
                                proceed = False

                            if proceed:
                                # We now need to create our package_branch
                                store_message(p, 'creating package_branch in MF')
                                branch = createpackagebranch(hub, p)
                                for errors in branch['errors']:
                                    store_message(p, errors + ': ' + branch['errors'][errors])
                                    proceed = False

                    if proceed:
                        # at this point we should have our package and branchs created
                        # lets go ahead and submit the build to MF
                        store_message(p, 'creating build %s in MF' % pkg_name)
                        build = createbuild(hub, p, config['user_label'], pkg_name)
                        for errors in build['errors']:
                            store_message(p, errors + ': ' + build['errors'][errors])
                            proceed = False

                # its now safe to delete the tmp location we were using
                shutil.rmtree(tmp)

        # set our URL cache back
        # this allows us to parse from top to bottom again
        content.seek(0)

    if args.email:
        # And finally we can use our stored message to email
        email(config['toaddr'], config['fromaddr'], pkgs)

if __name__ == '__main__':
    main()
