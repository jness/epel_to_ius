import os
from configobj import ConfigObj

def get_config():
    '''reads your ~/.epel_to_ius.conf and returns config'''

    # pull in our epel_to_ius Config
    c = os.path.expanduser('~/.epel_to_ius.conf')
    if os.path.exists(c):
        config = ConfigObj(c)

        if not config.has_key('baseurl'):
            raise Exception('baseurl not configured in ~/.epel_to_ius.conf')

        if not config.has_key('pkgfile'):
            raise Exception('pkgfile not configured in ~/.epel_to_ius.conf')

        if not config.has_key('cache_file'):
            raise Exception('cache_file not configured in ~/.epel_to_ius.conf')

        if not config.has_key('baseurl_cache'):
            raise Exception('baseurl_cache not configured in ~/.epel_to_ius.conf')

        if not config.has_key('toaddr'):
            raise Exception('toaddr not configured in ~/.epel_to_ius.conf')

        if not config.has_key('fromaddr'):
            raise Exception('fromaddr not configured in ~/.epel_to_ius.conf')

        if not config.has_key('user_label'):
            raise Exception('user_label not configured in ~/.epel_to_ius.conf')

        # return the config obj
        return config

    else:
        raise Exception('~/.epel_to_ius.conf not found')
