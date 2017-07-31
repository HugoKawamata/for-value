from lxml import html
import requests

def decode_message(message):
    cardList = message.split("\n")
    searchList = []
    for card in cardList:
        search = card.replace(",", "%2C")
        search = search.replace(" ", "+")
        search = search.replace("'", "%27s")
        search = search.replace(":", "%3A")
        search = search.replace("!", "%21")
        search = search.replace("&", "%26")
        searchList.append(search)
    return searchList

def get_prices(cardList):
    deetsList = []
    for card in cardList:
        cardDeets = {"name": "error", "edition": "error", "price": "error"}
        page = requests.get("http://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=" + card)
        tree = html.fromstring(page.content)

        name = tree.xpath("(//div[@class='col-sm-9 mainListing']//span[@class='productDetailTitle'])[1]//text()")[0]
        cardDeets["name"] = name

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
    for deet in deetsList:
        message += deet["name"] + ": "
        message += deet["price"] + "\n"
    return message