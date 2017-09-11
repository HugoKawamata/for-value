from lxml import html
import requests
from re import sub
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
import json
import sys


def determine_mode(message):
    if len(message.split()) > 0:
        if message.split()[0].lower() == "!help":
            return "help-mode"
        else:
            return "price-set-mode"
    else:
        return "price-set-mode"

def represents_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def find_quantity(card):
    """Takes a line of a message (called `card` in decodeMessage()) and returns a number
    which was specified at the start as the quantity of the card needed"""
    # If user specified quantity, set quantity
    if represents_int(card.split()[0]):
        if int(card.split()[0]) < 1:
            return 1
        else:
            return int(card.split()[0])
    else:
        return False # Players want one card by default, but return False to show quantity was not found

def message_to_currency_and_message(message):
    """Takes: a raw, untampered-with facebook message, possibly containing a currency command
    Returns: a dictionary with the currency specified and the message with the currency command removed"""
    currencyList = ["AUD","USD","BGN","BRL","CAD","CHF","CNY","CZK","DKK","GBP","HKD","HRK","HUF","IDR","ILS",
        "INR","JPY","KRW","MXN","MYR","NOK","NZD","PHP","PLN","RON","RUB","SEK","SGD","THB","TRY","ZAR","EUR"]
    # AUD by default
    currency = "AUD"

    # If the first character of the message is "!" and the first word is in the currency list, set the currency to that.
    if message.split()[0][0] == "!" and message.split()[0][1:].upper() in currencyList:
        currency = message.split()[0][1:].upper()
        message = message.replace(message.split()[0] + " ", "") # Then remove the first word (it's the currency command)
    message = message.lower().replace("!p ", "").replace("!s ", "") # In case anyone is still using old syntax, we should remove these strings.
    return {"currency": currency, "message": message}

def message_to_search_list(message):
    """Takes: a facebook message with the currency command removed
    Returns: a dictionary of searches, which will be fed into the Card Kingdom search engine"""
    searchList = []
    cardList = message.split("\n")
    for card in cardList:
        quantity = find_quantity(card)
        if quantity == False:
            quantity = 1
        else: # If quantity was specified, remove number
            card = card.replace(card.split()[0], "")

        search = card.replace(",", "%2C").replace(" ", "+").replace("'", "%27").replace(":", "%3A").replace("!", "%21").replace("&", "%26")
        if "\"" in card: # User is trying to use quotes to search for an exact name
            search = search.replace("\"", "")
            search = search + "%24" # This apparently pattern matches to "end of string" in card kingdom's search bar !! (I know its gross)
        if "!foil" in card:
            search = search.replace("%21foil+", "")
            search = search + "&filter[tab]=mtg_foil"
        searchList.append({"search": search, "quantity": quantity})
    return searchList


def get_prices(decodedMsg, getEdition):
    """Takes: decodedmessage: a facebook message that has been put through decode_message()
             which should be a dictionary like this: 
             {"currency": "USD", "searches": [{"search": "counterspell", "quantity": 1}]}.
             currency is a string representing a currency,
             searches is a list of dictionaries containing the search (the treated cardname) and the quantity
    Returns: a similar dictionary {"currency": "USD", "deets": deetsList}

    deetsList is a list of "deets", short for card details (from the search result),
    {"name": "cancel", "edition": "RTR", "price": "0.20"}"""
    deetsList = []
    for query in decodedMsg["searches"]:
        card = query["search"]
        resultNumber = 1

        # Initially search alphabetically, because "most popular" can result in Alpha and masterpiece cards showing up
        cardDeets = {"name": "error", "edition": "error", "price": "error", "quantity": query["quantity"]}
        page = requests.get("http://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=" + card)
        tree = html.fromstring(page.content)

        if "%24" in card: # The user wants to search for exactly this card.
            firstPageNames = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])//text()")
            name = "error" # Failsafe
            for gotname in firstPageNames: # Check all the names in the search results one by one
                # Convert search back to real english for string comparison
                realname = card.replace("%2C", ",").replace("+", " ").replace("%27", "'").replace("%3A", ":") \
                .replace("%21", "!").replace("%26", "&").replace("&filter[tab]=mtg_foil", "").replace("%24", "")

                # If the query and the result are "close enough" (0.8), return that result (and mark its number in the list)
                if SequenceMatcher(None, realname.lower(), gotname.lower()).ratio() > 0.8:
                    name = gotname
                else:
                    resultNumber += 1

        else: # User didn't put quotes in their search, so we do a smart search
            singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")
            name = singleItemList[0] if len(singleItemList) > 0 else "error" # If the single item list we get doesn't even have one item, throw an error.

            if "(" in name: # If it gets a funky result, like an emblem or a duel deck anthology result, we search most popular instead.
                page = requests.get("http://www.cardkingdom.com/catalog/search?filter%5Bipp%5D=20&filter%5Bsort%5D=most_popular&filter%5Bname%5D=" + card)
                tree = html.fromstring(page.content)

                singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")
                name = singleItemList[0] if len(singleItemList) > 0 else "error" # If the single item list we get doesn't even have one item, throw an error.


        cardDeets["name"] = name
        if "&filter[tab]=mtg_foil" in card: # This isn't triggered if the user directly inputs this string because the
                                            # "&" at the start is changed to "%26" lmao
            cardDeets["name"] = "FOIL " + cardDeets["name"]

        if getEdition:
            singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//div[@class='productDetailSet'])[" + str(resultNumber) + "]//text()")
            edition = singleItemList[0] if len(singleItemList) > 0 else "error"
            cardDeets["edition"] = " ".join(edition.split()) # Remove whitespace

        singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='stylePrice'])[" + str(((resultNumber - 1) * 4) + 1) + "]//text()")
        price = singleItemList[0] if len(singleItemList) > 0 else "error"
        cardDeets["price"] = " ".join(price.split())

        deetsList.append(cardDeets)
    
    result = {"currency": decodedMsg["currency"], "deets": deetsList}
    return result

def convert_price(price, quantity, currency):
    conversions = requests.get("http://api.fixer.io/latest?base=USD").text
    data = json.loads(conversions)
    try:
        decPrice = Decimal(sub(r'[^\d.]', '', price))
    except InvalidOperation:
        decPrice = 0.0
    decPrice *= quantity

    if currency.upper() == "USD":
        return "USD " + str(decPrice)
    else:
        decPrice = float(decPrice) * data["rates"][currency.upper()]
        return currency.upper() + " " + str(round(decPrice, 2))


def compose_message(message):
    reply = ""
    currencyMessage = message_to_currency_and_message(message)
    searchList = message_to_search_list(currencyMessage["message"])
    result = {"currency": currencyMessage["currency"], "searches": searchList}
    pricesResult = get_prices(result, True)
    totalCost = 0
    for deet in pricesResult["deets"]:
        if deet["name"] != "error" and deet["name"] != "FOIL error":
            if deet["quantity"] > 1:
                reply += str(deet["quantity"]) + " "
            reply += deet["name"]
            if deet["edition"] != "error":
                reply += " - " + deet["edition"]
            reply += ": "
            if deet["price"] != "error":
                newPrice = convert_price(deet["price"], deet["quantity"], pricesResult["currency"])
                reply += newPrice + "\n"
                totalCost += Decimal(sub(r'[^\d.]', '', newPrice))
    if len(pricesResult["deets"]) > 1:
        if reply == "":
            reply = "No cards were found for those searches. Please ensure spelling is correct, and try again. Type !help for help."
        else:
            reply += "Total Price: $" + str(totalCost)
    else:
        if reply == "":
            reply = "No cards were found for that search. Please ensure spelling is correct, and try again. Type !help for help."
    if len(reply) < 640:
        return reply
    else: 
        return "Whoa, too many cards. Facebook limits the length of text messages, so I can't send that result back. Try fewer cards."

def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()