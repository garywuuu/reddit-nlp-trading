import asyncpraw
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

import config
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import asyncio

API_KEY = config.API_KEY
SECRET_KEY = config.SECRET_KEY

trading_client = TradingClient(API_KEY, SECRET_KEY)

sia = SIA()

subreddit = 'ethereum'
headlines = set()
scores = []

subr_to_asset = {
  'ethereum' : 'ETH/USD'
}

reddit = asyncpraw.Reddit(
    client_id='oIE97p3JpStwi3zkhaHDbQ',
    client_secret='eTKyWcGQx4BbR5FIepquxMxBIdfcxA',
    redirect_uri="http://localhost:8080",
    user_agent="trading by u/notlarry12",
)

wait = 3000

async def main():
  while True:
    task1 = loop.create_task(get_headlines())
    # Wait for the tasks to finish
    await asyncio.wait([task1])

    task2 = loop.create_task(calculate_polarity())
    # Wait for the tasks to finish
    await asyncio.wait([task2])

    await trade()
    # # Wait for the value of waitTime between each quote request
    await asyncio.sleep(wait)

# each subreddit gets its own set of headlines within the headlines dictionary

# using reddit client, fetching new headlines within the given subreddit
async def get_headlines():
  try:
    for submission in reddit.subreddit(subreddit).new(limit=None):
        headlines.add(submission.title)
    print("got headlines")
    return True

  except Exception as e:
    print("There was an issue scraping reddit data: {0}".format(e))
    return False

# scoring the headlines
async def calculate_polarity():
  try:
    for line in headlines:
        pol_score = sia.polarity_scores(line)
        pol_score['headline'] = line
        scores = pol_score
    print("calculated polarity")
    return True
  except Exception as e:
    print("There was an issue calculating polarity: {}")
    return True

async def trade():
  mean = pd.DataFrame.from_records(scores).mean()
  print("Happy")
  return True


def post_order(subreddit : str):
  # prepare order
  try:
    market_order_data = MarketOrderRequest(
      symbol = subr_to_asset(subreddit), 
      qty=0.01,
      side=OrderSide.BUY,
      time_in_force=TimeInForce.DAY)

    market_order = trading_client.submit_order(
      order_data=market_order_data)
    
    print("Bought {}". subr_to_asset(subreddit))
    return market_order
  
  except Exception as e:
    print("Issue posting order to Alpaca: {}".format(e))
    return False

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()