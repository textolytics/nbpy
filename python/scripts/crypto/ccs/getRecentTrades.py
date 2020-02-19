import ccs

while True:
    response = ccs.kraken.public.getRecentTrades("XXBTZUSD")
    print(response)
