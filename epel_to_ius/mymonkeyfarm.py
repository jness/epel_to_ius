import os
from configobj import ConfigObj
from monkeyfarm.interface import MFAPIKeyRequestHandler, MFInterface

def get_connection(con_name='default'):
    '''parses your ~/.mf.conf for API key'''
    if not con_name:
        con_name = 'default'

    # pull in our epel_to_mf Config
    c = os.path.expanduser('~/.mf.conf')
    if os.path.exists(c):
        config = ConfigObj(c)
    else:
        raise Exception('~/.mf.conf not found')

    # Parse our config
    for sect in config.sections:
        if sect.startswith('connection:'):
            try:
                assert config[sect].has_key('user'), \
                    "Missing 'user' setting in %s (%s)." % (_file, sect)
                assert config[sect].has_key('api_key'), \
                    "Missing 'api_key' setting in %s (%s)." % (_file, sect)
                assert config[sect].has_key('url'), \
                    "Missing 'url' setting in %s (%s)." % (_file, sect)
            except AssertionError, e:
                raise e

            name = sect.split(':')[1]
            if name == con_name:
                api = {}
                api['api_key'] = config[sect]['api_key']
                api['user'] = config[sect]['user']
                api['url'] = config[sect]['url']
                return (api)
    else:
        return False


def connect():
    '''Connects to Monkey Farm'''
    config = get_connection(con_name='default')
    if config:
        rh = MFAPIKeyRequestHandler(config['url'])
        rh.auth(config['user'], config['api_key'])
        hub = MFInterface(request_handler=rh)
        return hub
    else:
        raise Exception('It does not appear you have a ~/.mf.conf')

def createpackagebranch(hub, p):
    branch = hub.package_branch.create(dict(
              label=p + '.master',
              project_label='ius',
              releases=['el5', 'el6'],
              package_label=p,
              url='bzr+ssh://bazaar.launchpad.net/~ius-coredev/ius/' + p.lower(),
              vcs_branch='',
              build_handler_label='rpm',
              build_prefix='',
              ))
    return branch

def createpackage(hub, p, user_label, summary):
    package = hub.package.create(dict(
              label=p,
              source_name=p,
              project_label='ius',
              user_label=user_label,
              summary=summary,
              group_label='ius-coredev',
              footprint=1,
              ))
    return package

def createbuild(hub, p, user_label, lab):
    build = hub.build.create(dict(
            label=lab,
            project_label='ius',
            package_branch_label=p + '.master',
            scratch=False,
            scratch_url='',
            user_label=user_label,
            pre_tag_label='testing-candidate',
            build_type_label='newpackage'
            ))
    return build
