from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()

    command_parser = parser.add_subparsers(
        dest='command',
        required=True
    )

    init_parser = command_parser.add_parser('init')
    init_parser.add_argument(
        '--dataset-sector',
        dest='dataset_sector',
        default='./data/raw/sectors'
    )
    init_parser.add_argument(
        '-D', '--debug',
        action='store_true',
        dest='debug'
    )

    daily_parser = command_parser.add_parser('daily')
    daily_parser.add_argument(
        '-D', '--debug',
        action='store_true',
        dest='debug'
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == 'init':
        from .market.init import run_init_market_pipeline
        from .strategy.init import run_init_strategy_pipeline

        run_init_market_pipeline(args)
        run_init_strategy_pipeline(args)

    elif args.command == 'daily':
        from .market.daily import run_daily_market_pipeline
        from .strategy.daily import run_daily_strategy_pipeline

        run_daily_market_pipeline(args)
        run_daily_strategy_pipeline(args)
