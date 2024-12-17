import datetime

from pyoanda import Client, PRACTICE, Order

client = Client(
    environment=PRACTICE,
    account_id='9276489',
    access_token='2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40'
)

test_order = Order(
    instrument="BCO_USD",
    units=1000,
    side="buy",
    type="market",
    trailingStop=51.10,
    takeProfit=58.55,
    # price=1.1100,
    # now = datetime.datetime.now()
    # expire = now + datetime.timedelta(days=1)
    # expiry="GTC"
    expiry = (datetime.datetime.now() + datetime.timedelta(days=50)).isoformat('T') + "Z"

    # expiry=(datetime.datetime.now() + datetime.timedelta(days=1))
    # expiry=datetime.datetime.now()

)

position = client.get_positions()
print (position)
order = client.create_order(order=test_order)