import os
import unittest

from configargparser import ArgumentConfigEnvParser

class TestParser(unittest.TestCase):

    def setUp(self):
        super(TestParser, self).setUp()
        fake_config = """
[MAIN]
foo:bar
bar:1
"""
        with open('_config.file', 'w') as fout:
            fout.write(fake_config)

        self.parser = parser = ArgumentConfigEnvParser()
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

        self.parser_defaults = {'foo': 'grape', 'bar': 7, 'baz': None, 'qux': 6}
        self.config_defaults = {'foo': 'bar', 'bar': 1}
        self.env_defaults = {'baz': 3.14159}

    def tearDown(self):
        super(TestParser, self).tearDown()
        try:
            # Some tests set this environment variable.
            del os.environ['BAZ']
        except KeyError:
            pass
        os.remove('_config.file')

    def test_parse_from_argparse_defaults(self):
        ns = self.parser.parse_args([])

        # This should be the defaults we gave the parser
        self.assertEqual(ns.__dict__, self.parser_defaults)

    def test_config_override(self):
        # This should be the defaults we gave the parser + config defaults
        d = self.parser_defaults
        d.update(self.config_defaults)
        ns = self.parser.parse_args(['--config-file', '_config.file'])
        self.assertDictEqual(ns.__dict__, d)

    def test_env_override(self):
        # This should be the parser defaults + config defaults + env_defaults
        os.environ['BAZ'] = '3.14159'

        d = self.parser_defaults
        d.update(self.config_defaults)
        d.update(self.env_defaults)
        ns = self.parser.parse_args(['--config-file', '_config.file'])
        self.assertDictEqual(ns.__dict__, d)

    def test_commandline_override(self):
        # This should be the parser defaults + config defaults +
        #                    env_defaults + commandline
        os.environ['BAZ'] = '3.14159'
        commandline = {'foo': '3', 'qux': 4}
        d = self.parser_defaults
        d.update(self.config_defaults)
        d.update(self.env_defaults)
        d.update(commandline)
        ns = self.parser.parse_args(['--config-file', '_config.file',
                                     '--foo=3', '--qux=4'])
        self.assertDictEqual(ns.__dict__, d)


if __name__ == '__main__':
    unittest.main()
