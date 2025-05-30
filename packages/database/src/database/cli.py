from argparse import ArgumentParser, Namespace
from database import create_database, enable_debug


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        dest='debug'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        enable_debug()

    create_database()
