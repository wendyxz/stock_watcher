import requests
from twilio.rest import Client
import config

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API_KEY = config.STOCK_API_KEY
NEWS_API_KEY = config.NEWS_API_KEY

TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN

PERCENT_CHANGE = 10

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]

# need to convert dict into list, because date changes everyday and we can't hard code to get key value
data_lst = [value for (key, value) in data.items()]

yesterday_data = data_lst[0]
yesterday_close = float(yesterday_data["4. close"])

day_before_yesterday_data = data_lst[1]
day_before_yesterday_close = float(day_before_yesterday_data["4. close"])

diff = day_before_yesterday_close - yesterday_close

up_down = None
if diff < 0:
    up_down = "🔺"
else:
    up_down = "🔻"

diff = abs(diff)

per_diff = diff / day_before_yesterday_close * 100

if per_diff > PERCENT_CHANGE:
    news_params = {
        "apiKEY": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params, timeout=5)
    news_data = news_response.json()
    articles = news_data["articles"]
    three_articles = articles[:3]

    formatted_articles = [f"{STOCK_NAME}: {up_down}{round(per_diff, 2)}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages \
            .create(
            body=article,
            from_=config.TWILIO_NUMBER,
            to=config.MY_NUMBER
        )
        print(message.status)




