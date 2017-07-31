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
    for card in cardList:
        page = requests.get("http://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=" + card)
        tree = html.fromstring(page.content)
        name = "".join(tree.xpath('//div[@class="mainListing"][1]//span[@class="productDetailTitle"][1]/a/text()'))
        return name