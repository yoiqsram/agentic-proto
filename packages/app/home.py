import streamlit as st
from datetime import datetime

from src.model.asset import StockOHLCV, StockAsset, StockBalance, CashBalance
from src.model.trade import StockAction, StockTrade
from src.model.user import User


user = User(
    username='yoiqsram',
    full_name='Yoiq S Rambadian',
    created_datetime=datetime.now()
)

cash_balance = CashBalance(
    username=user.username,
    balance_before=0,
    balance_after=7_000_000,
    balance_datetime=datetime.now()
)
stocks_data = {
    'BBCA': StockOHLCV(
        code='BBCA',
        open=999,
        high=999,
        low=999,
        close=999,
        volume=999_999
    ),
    'TLKM': StockOHLCV(
        code='TLKM',
        open=999,
        high=999,
        low=999,
        close=999,
        volume=999_999
    ),
    'PTBA': StockOHLCV(
        code='PTBA',
        open=999,
        high=999,
        low=999,
        close=999,
        volume=999_999
    ),
}
stocks_owned = StockBalance(
    username='dummy',
    assets=[
        StockAsset(
            code='BBCA',
            amount=5
        ),
        StockAsset(
            code='TLKM',
            amount=12
        ),
        StockAsset(
            code='PTBA',
            amount=20
        ),
    ]
)

pending_trades = [
    StockTrade(
        asset=StockAsset(
            code='BBRI',
            amount=10
        ),
        action=StockAction.BUY,
        price=1000,
        commission_fee=0.002,
        created_datetime=datetime.now()
    ),
]


st.markdown("""\
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


with st.container(border=True):
    st.subheader(f'Hello, {user.full_name}!')

    stock_balance = sum(
        stock_owned.amount * stocks_data[stock_owned.code].close * 100
        for stock_owned in stocks_owned.assets
    )
    total_wealth = cash_balance.balance_after + stock_balance

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            '🏦 Total Wealth',
            f'IDR {total_wealth:,.2f}'
        )

    with col2:
        st.metric(
            '📈 Annual ROI',
            f'+4.28%'
        )

    col3, col4 = st.columns(2)
    with col3:
        st.metric(
            '💵 Cash Balance',
            f'IDR {cash_balance.balance_after:,.2f}'
        )

    with col4:
        st.metric(
            '💸 Stock Balance',
            f'IDR {stock_balance:,.2f}'
        )

    _, col_edit = st.columns([4, 1])
    with col_edit:
        st.button(
            'Edit',
            key=f'edit-wealth',
            use_container_width=True
        )


with st.expander(f'Stocks Owned ({len(stocks_owned.assets)})', icon='📈'):
    if len(stocks_owned.assets) > 0:
        _, col_add = st.columns([4, 1])
        with col_add:
            st.button(
                'Add',
                key=f'add-stock-owned',
                type='primary',
                use_container_width=True
            )

        for i, stock_owned in enumerate(stocks_owned.assets):
            with st.container(border=True):
                st.markdown(f'''\
                **{stock_owned.code}**

                - Amount: {stock_owned.amount}
                - Price: {stocks_data[stock_owned.code].close}
                - Total: IDR {stock_owned.amount * stocks_data[stock_owned.code].close * 100:,.2f}
                - ROI: {stocks_data[stock_owned.code].close / stocks_data[stock_owned.code].close * 100 - 100:.2f}%
                ''')

                _, col_action = st.columns([4, 1])
                with col_action:
                    st.button(
                        'Sell',
                        key=f'sell-{stock_owned.code}-{i:03d}',
                        use_container_width=True
                    )

    else:
        st.text("You don't own any stock.")
        _, col_add, _ = st.columns([2, 1, 2])
        with col_add:
            st.button(
                'Add',
                key=f'add-stock-owned',
                type='primary',
                use_container_width=True
            )

if len(pending_trades) > 0:
    with st.expander(f'Pending trades ({len(pending_trades)})', icon='⏳'):
        for i, stock_trade in enumerate(pending_trades):
            with st.container(border=True):
                st.markdown(f'''\
                **{stock_trade.asset.code}**

                - Datetime: {stock_trade.created_datetime}
                - Amount: {stock_trade.asset.amount}
                - Price: {stock_trade.price}
                - Total: IDR {stock_trade.asset.amount * stock_trade.price:,.2f}
                ''')

                _, col_action = st.columns([4, 1])
                with col_action:
                    st.button(
                        'Confirm',
                        key=f'confirm-trade-{stock_trade.asset.code}-{i:03d}',
                        type='primary',
                        use_container_width=True
                    )

recommended_trades = [
    StockTrade(
        asset=StockAsset(
            code='TLKM',
            amount=12,
        ),
        action=StockAction.SELL,
        price=stocks_data['TLKM'].close,
        commission_fee=0.018,
        created_datetime=datetime.now()
    ),
    StockTrade(
        asset=StockAsset(
            code='BBCA',
            amount=15,
        ),
        action=StockAction.BUY,
        price=stocks_data['BBCA'].close,
        commission_fee=0.02,
        created_datetime=datetime.now()
    ),
]


with st.container(border=True):
    st.subheader('📌 Top Recommendation')
    st.text('🗓️ ' + datetime.now().strftime('%Y-%m-%d'))

    for i, recommended_trade in enumerate(recommended_trades):
        with st.container(border=True):
            st.markdown(f'''\
            **{recommended_trade.asset.code}**

            - Datetime: {recommended_trade.created_datetime}
            - Amount: {recommended_trade.asset.amount}
            - Price: {recommended_trade.price}
            - Total: IDR {recommended_trade.asset.amount * recommended_trade.price:,.2f}
            ''')

            with st.expander('Read analysis'):
                st.markdown(
                    'Lorem ipsum dolor sit amet, consectetur adipiscing '
                    'elit. Sed do eiusmod tempor incididunt ut labore et '
                    'dolore magna aliqua. Ut enim ad minim veniam, quis '
                    'nostrud exercitation ullamco laboris nisi ut aliquip '
                    'ex ea commodo consequat. Duis aute irure dolor in '
                    'reprehenderit in voluptate velit esse cillum dolore '
                    'eu fugiat nulla pariatur. Excepteur sint occaecat '
                    'cupidatat non proident, sunt in culpa qui officia '
                    'deserunt mollit anim id est laborum.'
                )

            _, col_action = st.columns([4, 1])
            with col_action:
                st.button(
                    'Checkout',
                    key=f'checkout-trade-{recommended_trade.asset.code}-{i:03d}',
                    type='primary',
                    use_container_width=True
                )
