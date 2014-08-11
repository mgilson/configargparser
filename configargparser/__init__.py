import argparse
import ConfigParser
import os

def _identity(x):
    return x

_SENTINEL = object()
_CONFIG_MISSING_OPT_ERRORS = (ConfigParser.NoSectionError,
                              ConfigParser.NoOptionError)

class AddConfigFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # I can never remember if `values` is a list all the time or if it
        # can be a scalar string; this takes care of both.
        if isinstance(values,basestring):
            parser.config_files.append(values)
        else:
            parser.config_files.extend(values)


class ArgumentConfigEnvParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        """
        Added 2 new keyword arguments to the ArgumentParser constructor:

           config --> List of filenames to parse for config goodness
           default_section --> name of the default section in the config file
        """
        self.config_files = kwargs.pop('config',[])  #Must be a list
        self.default_section = kwargs.pop('default_section', 'MAIN')
        self._action_defaults = {}
        super(ArgumentConfigEnvParser, self).__init__(*args, **kwargs)


    def add_argument(self, *args, **kwargs):
        """
        Works like `ArgumentParser.add_argument`, except that we've added an action:

           config: add a config file to the parser

        This also adds the ability to specify which section of the config file to pull the
        data from, via the `section` keyword.  This relies on the (undocumented) fact that
        `ArgumentParser.add_argument` actually returns the `Action` object that it creates.
        We need this to reliably get `dest` (although we could probably write a simple
        function to do this for us).
        """

        if 'action' in kwargs and kwargs['action'] == 'config':
            kwargs['action'] = AddConfigFile
            kwargs['default'] = argparse.SUPPRESS

        # argparse won't know what to do with the section, so
        # we'll pop it out and add it back in later.
        #
        # We also have to prevent argparse from doing any type conversion,
        # which is done explicitly in parse_known_args.
        #
        # This way, we can reliably check whether argparse has replaced the
        # default.
        #
        section = kwargs.pop('section', self.default_section)
        type = kwargs.pop('type', _identity)
        default = kwargs.pop('default', _SENTINEL)

        if default is not argparse.SUPPRESS:
            kwargs.update(default=_SENTINEL)
        else:
            kwargs.update(default=argparse.SUPPRESS)

        action = super(ArgumentConfigEnvParser, self).add_argument(
            *args, **kwargs)
        kwargs.update(section=section, type=type, default=default)
        self._action_defaults[action.dest] = (args, kwargs)
        return action

    def parse_known_args(self, args=None, namespace=None):
        ns, argv = super(ArgumentConfigEnvParser, self).parse_known_args(
            args=args, namespace=namespace)
        config_parser = ConfigParser.SafeConfigParser()
        config_files = [os.path.expanduser(os.path.expandvars(x))
                        for x in self.config_files]
        config_parser.read(config_files)

        for dest, (args, init_dict) in self._action_defaults.items():
            type_converter = init_dict['type']
            default = init_dict['default']
            obj = default

            if getattr(ns, dest, _SENTINEL) is not _SENTINEL: # command line
                obj = getattr(ns, dest)
            else: # not on commandline
                try:  # get from config file
                    obj = config_parser.get(init_dict['section'], dest)
                except _CONFIG_MISSING_OPT_ERRORS: # Nope, not in config file
                    try: # get from environment
                        obj = os.environ[dest.upper()]
                    except KeyError:
                        pass

            if obj is _SENTINEL:
                setattr(ns, dest, None)
            elif obj is argparse.SUPPRESS:
                pass
            else:
                setattr(ns, dest, type_converter(obj))

        return ns, argv


if __name__ == '__main__':
    #TODO:  Make these real unittests.
    fake_config = """
[MAIN]
foo:bar
bar:1
"""
    with open('_config.file', 'w') as fout:
        fout.write(fake_config)

    parser = ArgumentConfigEnvParser()
    parser.add_argument('--config-file', action='config',
                        help='location of config file')
    parser.add_argument('--foo', type=str, action='store', default='grape',
                        help="don't know what foo does ...")
    parser.add_argument('--bar', type=int, default=7, action='store',
                        help='This is an integer (I hope)')
    parser.add_argument('--baz', type=float, action='store',
                        help='This is a float (I hope)')
    parser.add_argument('--qux', type=int, default='6', action='store',
                        help='this is another int')
    ns = parser.parse_args([])

    parser_defaults = {'foo': "grape", 'bar': 7, 'baz': None, 'qux': 6}
    config_defaults = {'foo': 'bar', 'bar': 1}
    env_defaults = {"baz": 3.14159}

    # This should be the defaults we gave the parser
    print ns
    assert ns.__dict__ == parser_defaults

    # This should be the defaults we gave the parser + config defaults
    d = parser_defaults.copy()
    d.update(config_defaults)
    ns = parser.parse_args(['--config-file', '_config.file'])
    print ns
    assert ns.__dict__ == d

    os.environ['BAZ'] = '3.14159'

    # This should be the parser defaults + config defaults + env_defaults
    d = parser_defaults.copy()
    d.update(config_defaults)
    d.update(env_defaults)
    ns = parser.parse_args(['--config-file', '_config.file'])
    print ns
    assert ns.__dict__ == d

    # This should be the parser defaults + config defaults +
    #                    env_defaults + commandline
    commandline = {'foo': '3', 'qux': 4}
    d = parser_defaults.copy()
    d.update(config_defaults)
    d.update(env_defaults)
    d.update(commandline)
    ns = parser.parse_args(['--config-file', '_config.file',
                            '--foo=3', '--qux=4'])
    print ns
    assert ns.__dict__ == d

    os.remove('_config.file')
