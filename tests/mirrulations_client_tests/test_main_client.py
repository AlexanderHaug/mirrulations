import argparse
from mock import patch

from mirrulations_client.__main__ import main, parse_args


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


@patch('mirrulations_client.__main__.os.path.exists', return_value=True)
def test_main_no_config_setup(ospe):
    with patch('mirrulations_client.__main__.parse_args',
               return_value={'config': False}) as pa, \
         patch('mirrulations_client.__main__.run_client') as rc:
        main()
        assert pa.called
        assert rc.called


@patch('mirrulations_client.__main__.os.path.exists', return_value=False)
def test_main_with_config_setup(ospe):
    with patch('mirrulations_client.__main__.parse_args',
               return_value={'config': True}) as pa, \
         patch('mirrulations_client.__main__.client_config_setup') as ccs, \
         patch('mirrulations_client.__main__.run_client') as rc:
        main()
        assert pa.called
        assert ccs.called
        assert rc.called
