import ccs
import simplejson as json
response = ccs.kraken.public.getTradableAssetPairs ()

msg=json.loads(response)
instruments = msg['result']
count =0
for instrument in instruments:
    instrument = str(instrument)
    instrument_details = instruments[instrument]
    altname = instrument_details['altname']
    aclass_base = instrument_details['aclass_base']
    base = instrument_details['base']
    aclass_quote = instrument_details['aclass_quote']
    quote = instrument_details['quote']
    lot = instrument_details['lot']
    pair_decimals = instrument_details['pair_decimals']
    lot_decimals = instrument_details['lot_decimals']
    lot_multiplier = instrument_details['lot_multiplier']
    leverage_buy = instrument_details['leverage_buy']
    leverage_sell = instrument_details['leverage_sell']
    fee_volume_currency = instrument_details['fee_volume_currency']
    margin_call = instrument_details['margin_call']
    margin_stop = instrument_details['margin_stop']
    margin_call = instrument_details['margin_call']
    margin_stop = instrument_details['margin_stop']
    count = count + 1
    print(count,instrument,altname,aclass_base,base,aclass_quote,quote,lot,pair_decimals,lot_decimals,lot_multiplier,leverage_buy,leverage_sell,fee_volume_currency,margin_call,margin_stop,margin_call,margin_stop)
