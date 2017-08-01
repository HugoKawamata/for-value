from lxml import html
import requests
from re import sub
from decimal import Decimal

def determine_mode(message):
    if len(message.split()) > 0:
        if message.split()[0].lower() == "!p":
            return "price-mode"
        elif message.split()[0].lower() == "!s":
            return "price-set-mode"
        else:
            return "help-mode"
    else:
        return "help-mode"


def decode_message(message):
    demodedMessage = message.replace("!p", "").replace("!s", "")
    cardList = demodedMessage.split("\n")
    searchList = []
    for card in cardList:
        search = card.replace(",", "%2C").replace(" ", "+").replace("'", "%27s").replace(":", "%3A").replace("!", "%21").replace("&", "%26")
        searchList.append(search)
    return searchList

def get_prices(cardList, getEdition):
    deetsList = []
    for card in cardList:

        cardDeets = {"name": "error", "edition": "error", "price": "error"}
        page = requests.get("http://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=" + card)
        tree = html.fromstring(page.content)

        singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")
        name = singleItemList[0] if len(singleItemList) > 0 else "error"
        cardDeets["name"] = name

        if getEdition:
            singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//div[@class='productDetailSet'])[1]//text()")
            edition = singleItemList[0] if len(singleItemList) > 0 else "error"
            cardDeets["edition"] = " ".join(edition.split()) # Remove whitespace

        singleItemList = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='stylePrice'])[1]//text()")
        price = singleItemList[0] if len(singleItemList) > 0 else "error"
        cardDeets["price"] = " ".join(price.split())

        deetsList.append(cardDeets)
    
    return deetsList

def compose_message(deetsList):
    message = ""
    totalCost = 0
    for deet in deetsList:
        message += deet["name"]
        if deet["edition"] != "error":
            message += " - " + deet["edition"]
        message += ": "
        message += deet["price"] + "\n"
        if deet["price"] != "error":
            totalCost += Decimal(sub(r'[^\d.]', '', deet["price"]))
    if len(deetsList) > 1:
        message += "Total Price: $" + str(totalCost)
    return message