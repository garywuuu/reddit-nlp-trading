import praw
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


subreddit1, subreddit2 = 'ethereum', 'bitcoin'

headlines = {
  subreddit1 : set(),
  subreddit2 : set()
}

scores = {
  subreddit1 : [],
  subreddit2 : []
}


subr_to_asset = {
  'ethereum' : 'ETH/USD',
  'bitcoin' : 'BTC/USD'
}

reddit = praw.Reddit(client_id='Z6J1ZDT3fApjnmrHiMU6qw',
                     client_secret='jU7Oa-qfcU8od4X9E-6s0CwQp1tmEA',
                     user_agent='alpacatradoor')

wait = 3000

async def main():
  while True:
    task1 = loop.create_task(get_headlines(subreddit1))
    task2 = loop.create_task(get_headlines(subreddit2))
    # Wait for the tasks to finish

    task3 = loop.create_task(calculate_polarity(subreddit1))
    task4 = loop.create_task(calculate_polarity(subreddit2))
    # Wait for the tasks to finish
    # Wait for the task to finish
    await asyncio.wait([task1, task2, task3, task4])
    await trade()
    # # Wait for the value of waitTime between each quote request
    await asyncio.sleep(wait)

# each subreddit gets its own set of headlines within the headlines dictionary

# using reddit client, fetching new headlines within the given subreddit
async def get_headlines(subreddit : str):
  try:
    for submission in reddit.subreddit(subreddit).new(limit=None):
        headlines[subreddit].add(submission.title)
    print("hello")
    return True

  except Exception as e:
    print("There was an issue scraping reddit data: {0}".format(e))
    return False

# scoring the headlines
async def calculate_polarity(subreddit : str):
  for line in headlines[subreddit]:
      pol_score = sia.polarity_scores(line)
      pol_score['headline'] = line
      scores[subreddit] = pol_score
  return True

async def trade():
  df1 = pd.DataFrame.from_records(scores[subreddit1]).mean()
  df2 = pd.DataFrame.from_records(scores[subreddit2]).mean()
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
    
    print("Bought {}".format(subr_to_asset(subreddit)))
    return market_order
  
  except Exception as e:
    print("Issue posting order to Alpaca: {}".format(e))
    return False

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()