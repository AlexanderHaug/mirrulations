import argparse
from mock import patch

from mirrulations_server.__main__ import main, parse_args


def test_parse_args_no_arguments():
    with patch('argparse.ArgumentParser.parse_args',
               return_value=argparse.Namespace(config=False)):
        args = parse_args()
        assert len(args) == 1
        assert not args['config']


def test_parse_args_config():
    with patch('argparse.ArgumentParser.parse_args',
               return_value=argparse.Namespace(config=True)):
        args = parse_args()
        assert len(args) == 1
        assert args['config']


@patch('mirrulations_server.__main__.os.path.exists', return_value=True)
def test_main_no_config_setup(ospe):
    with patch('mirrulations_server.__main__.parse_args',
               return_value={'config': False}) as pa, \
         patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main()
        assert pa.called
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called


@patch('mirrulations_server.__main__.os.path.exists', return_value=False)
def test_main_with_config_setup(ospe):
    with patch('mirrulations_server.__main__.parse_args',
               return_value={'config': False}) as pa, \
         patch('mirrulations_server.__main__.server_config_setup') as scs, \
         patch('mirrulations_server.__main__.os.system') as redis, \
         patch('mirrulations_server.__main__.run') as endpoints, \
         patch('mirrulations_server.__main__.monolith') as dwg, \
         patch('mirrulations_server.__main__.expire') as expire:
        main()
        assert pa.called
        assert scs.called
        assert redis.called
        assert endpoints.called
        assert dwg.called
        assert expire.called
