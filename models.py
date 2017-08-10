from lxml import html
import requests
from re import sub
from decimal import Decimal
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


def decode_message(message):
    currencyList = ["AUD","USD","BGN","BRL","CAD","CHF","CNY","CZK","DKK","GBP","HKD","HRK","HUF","IDR",
        "ILS","INR","JPY","KRW","MXN","MYR","NOK","NZD","PHP","PLN","RON","RUB","SEK","SGD","THB","TRY","ZAR","EUR"]
    # AUD by default
    currency = "AUD"

    # If the first character of the message is "!" and the first word is in the currency list, set the currency to that.
    if message.split()[0][0] == "!" and message.split()[0][1:].upper() in currencyList:
        currency = message.split()[0][1:].upper()
        message = message.replace(message.split()[0], "") # Then remove the first word (it's the currency command)
    demodedMessage = message.lower().replace("!p", "").replace("!s", "") # In case anyone is still using old syntax, we should remove these strings.
    cardList = demodedMessage.split("\n")
    searchList = []
    for card in cardList:
        search = card.replace(",", "%2C").replace(" ", "+").replace("'", "%27").replace(":", "%3A").replace("!", "%21").replace("&", "%26")
        if "!foil" in card:
            search = search.replace("%21foil", "")
            search = search + "&filter[tab]=mtg_foil"
        searchList.append(search)
    result = {"currency": currency, "searches": searchList}
    log(result)
    return result

def get_prices(decodedMsg, getEdition):
    deetsList = []
    for card in decodedMsg["searches"]:

        # Initially search alphabetically, because "most popular" can result in Alpha and masterpiece cards showing up
        cardDeets = {"name": "error", "edition": "error", "price": "error"}
        page = requests.get("http://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=" + card)
        tree = html.fromstring(page.content)

        singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")
        name = singleItemList[0] if len(singleItemList) > 0 else "error" # If the single item list we get doesn't even have one item, throw an error.

        if "(" in name: # If it gets a funky result, like an emblem or a duel deck anthology result, we search most popular instead.
            page = requests.get("http://www.cardkingdom.com/catalog/search?filter%5Bipp%5D=20&filter%5Bsort%5D=most_popular&filter%5Bname%5D=" + card)
            tree = html.fromstring(page.content)

            singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")
            name = singleItemList[0] if len(singleItemList) > 0 else "error" # If the single item list we get doesn't even have one item, throw an error.


        cardDeets["name"] = name

        if getEdition:
            singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//div[@class='productDetailSet'])[1]//text()")
            edition = singleItemList[0] if len(singleItemList) > 0 else "error"
            cardDeets["edition"] = " ".join(edition.split()) # Remove whitespace

        singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='stylePrice'])[1]//text()")
        price = singleItemList[0] if len(singleItemList) > 0 else "error"
        cardDeets["price"] = " ".join(price.split())

        deetsList.append(cardDeets)
    
    result = {"currency": decodedMsg["currency"], "deets": deetsList}
    return result

def convert_price(price, currency):
    conversions = requests.get("http://api.fixer.io/latest?base=USD").text
    data = json.loads(conversions)
    decPrice = Decimal(sub(r'[^\d.]', '', price))

    if currency.upper() == "USD":
        log(decPrice)
        return "USD " + str(decPrice)
    else:
        decPrice = float(decPrice) * data["rates"][currency.upper()]
        return currency.upper() + " " + str(round(decPrice, 2))


def compose_message(pricesResult):
    message = ""
    totalCost = 0
    for deet in pricesResult["deets"]:
        if deet["name"] != "error":
            message += deet["name"]
            if deet["edition"] != "error":
                message += " - " + deet["edition"]
            message += ": "
            #message += deet["price"] + "\n"
            if deet["price"] != "error":
                newPrice = convert_price(deet["price"], pricesResult["currency"])
                message += newPrice + "\n"
                totalCost += Decimal(sub(r'[^\d.]', '', newPrice))
    if len(pricesResult["deets"]) > 1:
        if message == "":
            message = "No cards were found for those searches. Please ensure spelling is correct, and try again."
        else:
            message += "Total Price: $" + str(totalCost)
    else:
        if message == "":
            message = "No cards were found for that search. Please ensure spelling is correct, and try again."
    return message

def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()