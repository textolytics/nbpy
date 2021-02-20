SELECT DISTINCT
 (instrument) ins, avg(bid), avg(ask) 
FROM oanda_tick_view 
GROUP BY ins,bid,ask
LIMIT 150;

CREATE CONTINUOUS VIEW oanda_tick_view 
AS SELECT timestmp,instrument,bid,ask 
FROM oanda_tick;

CREATE CONTINUOUS VIEW oanda_last_tick_view
AS SELECT DISTINCT (instrument), max(timestmp),bid,ask
FROM oanda_tick
GROUP BY instrument,bid,ask
;

CREATE STREAM oanda_tick (timestmp timestamp, instrument text, bid float, ask float);

CREATE CONTINUOUS VIEW oanda_tick_view
AS SELECT timestmp,instrument,bid,ask
FROM oanda_tick;

SELECT DISTINCT(instrument),timestmp,bid,ask FROM oanda_tick_view;

DROP STREAM oanda_tick;

CREATE USER oanda

DROP CONTINUOUS VIEW oanda_last_tick_view;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO oanda;

CREATE CONTINUOUS VIEW oanda_last_tick_transform AS
SELECT DISTINCT instrument, MAX(timestmp), bid, ask
FROM oanda_tick
GROUP BY instrument, bid, ask;

SELECT * FROM oanda_last_tick_view;