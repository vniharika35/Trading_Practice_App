import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
import yfinance as yf
import random
from flask import current_app



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# def getQuote(quote):
#         return {
#             "name": quote["companyName"],
#             "price": float(quote["latestPrice"]),
#             "symbol": quote["symbol"]
#         }

# def lookup(symbol):
#     """Look up quote for symbol."""

#     # Contact API
#     try:
#         api_key = os.environ.get("API_KEY")
#         #response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
#         #response.raise_for_status()
#         stock = yf.Ticker(symbol)  # Replace with any stock symbol
#         print(stock.fast_info["last_price"])  # Fetch live stock price
#     except requests.RequestException:
#         return None

#     # Parse response
#     try:
#         quote = response.json()
#         return getQuote(quote)
#     except (KeyError, TypeError, ValueError):
#         return None

#def getQuote(ticker):
#    """Fetch stock data using yfinance"""
#    try:
#        stock = yf.Ticker(ticker)
#        #print("============================ Stocks Price for Ticketr" + ticker + " - " + stock.fast_info["last_price"])
#        return {
#            "name": stock.info.get("longName", "N/A"),  # Get company name
#            "price": stock.fast_info["last_price"],  # Fetch latest live price
#            "symbol": ticker.upper()
#        }
#    except Exception as e:
#        print(f"Error fetching data for {ticker}: {e}")
#        return None


def getQuote(ticker):
    """Fetch stock data using yfinance, optionally simulating the price."""
    try:
        stock = yf.Ticker(ticker)
        live_price = stock.fast_info["last_price"]
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None
    
    if ( live_price == None ):
        return None

    # Check the Flask configuration for simulation mode
    if current_app.config.get("SIMULATION_MODE", False):
        price_to_use = simulate_price(live_price)
    else:
        price_to_use = live_price

    return {
        "name": stock.info.get("longName", "N/A"),
        "price": price_to_use,
        "symbol": ticker.upper()
    }


def lookup(symbol):
    """Look up quote for symbol."""
    return getQuote(symbol)


# def lookups(symbolsList):

#     print(f"symbolsList:    {symbolsList}")
#     if len(symbolsList) == 0:
#         return {}

#     s = ""
#     for i in range(len(symbolsList)-1):
#         s = s + symbolsList[i] + ","

#     s = s + symbolsList[len(symbolsList)-1]

#     try:
#         api_key = os.environ.get("API_KEY")
#         response = requests.get(f"https://cloud.iexapis.com/v1/stock/market/batch?&types=quote&symbols={s}&token={api_key}")
#         response.raise_for_status()
#     except requests.RequestException:
#         return None

#     # Parse response
#     try:
#         symbolsQuotes = response.json()
#         quotesDict = {}

#         for symbol in symbolsList:
#             quotesDict[symbol] = getQuote(symbolsQuotes[symbol]["quote"])

#         #print(f"quotesDict: \n{quotesDict}")
#         return quotesDict
#     except (KeyError, TypeError, ValueError):
#         return None

#def lookups(symbolsList):
#    """Look up quotes for a list of symbols using yfinance."""
#    
#    print(f"=============symbolsList: {symbolsList}")
#    
#    if not symbolsList:  # If empty list, return empty dict
#        return {}
#
#    # Fetch multiple stocks at once using yfinance (recommended for batch processing)
#    try:
#        stocks = yf.Tickers(" ".join(symbolsList))  # Fetch multiple tickers
#        quotesDict = {}
#        print("Stocks Prices for SymbolList")
#        print(stocks)
#
#        for symbol in symbolsList:
#            stock = stocks.tickers.get(symbol)
#            print(stock.fast_info.get("last_price"))
#            if stock:
#                quotesDict[symbol] = {
#                    "name": stock.info.get("longName", "N/A"),
#                    "price": stock.fast_info["last_price"],
#                    "symbol": symbol.upper()
#                }
#            else:
#                quotesDict[symbol] = None  # If stock not found
#
#        return quotesDict
#    except Exception as e:
#        print(f"Error fetching stock data: {e}")
#        return None


def lookups(symbolsList):
    """Look up quotes for a list of symbols using yfinance."""
    if not symbolsList:
        return {}

    try:
        stocks = yf.Tickers(" ".join(symbolsList))
        quotesDict = {}

        for symbol in symbolsList:
            stock = stocks.tickers.get(symbol)
            if stock:
                live_price = stock.fast_info["last_price"]
                # Check the config for simulation mode
                price = simulate_price(live_price) if current_app.config.get("SIMULATION_MODE", False) else live_price
                quotesDict[symbol] = {
                    "name": stock.info.get("longName", "N/A"),
                    "price": price,
                    "symbol": symbol.upper()
                }
            else:
                quotesDict[symbol] = None

        return quotesDict
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def simulate_price(baseline, volatility=0.02):
    """
    Simulate a price based on a baseline value.
    volatility: Maximum percentage change (2% default)
    """
    change_percent = random.uniform(-volatility, volatility)
    return baseline * (1 + change_percent)



