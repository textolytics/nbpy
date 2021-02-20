CREATE STREAM twitter_tweet(
timestmp timestamp,
tweet_id text,
positive_score float, 
negative_score float,
time_zone text,
location_name text, 
user_name text,
statuses_count integer,
followers_count integer, 
lang text,
text text);

SELECT timestmp, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count,tweet_language, tweet 
from twitter_tweet_view
order by timestmp 
desc
LIMIT 100;

--oanda----------------------------------------------------
SELECT * FROM oanda_tick_view limit 100;

CREATE CONTINUOUS VIEW oanda_tick_view_minute AS
SELECT minute(timestmp), COUNT(*) 
FROM oanda_tick 
GROUP BY minute 
limit 100;

select * from oanda_tick_view_minute limit 100;

DROP CONTINUOUS VIEW oanda_tick_view_minute;
--
SELECT
		CAST (left(replace(replace(timestmp, '-',''), 'T',''), 10) as integer) as hours,
		(array_agg(bid ORDER BY timestmp ASC))[1] op,
		(array_agg(bid ORDER BY timestmp DESC))[1] cl
		FROM oanda_tick
		where instrument like 'AUD_CAD'
		GROUP BY hours
		ORDER BY hours
		desc

		;


--twitter----------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO twitter;

CREATE CONTINUOUS VIEW twitter_tweet_view
AS SELECT 
timestmp, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count,tweet_language, tweet
FROM twitter_stream_tweets;

DROP CONTINUOUS VIEW twitter_tweet_view

DROP STREAM twitter_tweet;

SELECT * FROM twitter_tweet_view LIMIt 100;
