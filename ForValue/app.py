import os
import sys
import json

import requests
from flask import Flask, request

from models import *

app = Flask(__name__)

@app.route('/testmessage', methods=['GET'])
def testmessage():
    return app.send_static_file("testmessage.html")

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return app.send_static_file("privacy.html")

@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    mode = determine_mode(message_text)

                    if os.environ.get("PAGE_ACCESS_TOKEN") == None: # We're testing
                        if mode == "price-set-mode":
                            reply = compose_message(message_text) # return a string of the message
                            log(reply)
                            #return reply
                        else:
                            helpMsg = "You can type cardnames on multiple lines in the same message to get a price sum.\n\n" + \
                                    "Currency Conversion: !USD (or your currency code) at the beginning of the message.\n\n" + \
                                    "Foils: !foil before the cardname will grab a foil version of that card.\n\n" + \
                                    "Prices are taken from www.cardkingdom.com"
                            log(helpMsg)
                            return(helpMsg)
                    else:
                        if mode == "price-set-mode":
                            respond = compose_message(message_text)
                        else:
                            respond = "You can type cardnames on multiple lines in the same message to get a price sum.\n\n" + \
                                    "Currency Conversion: !USD (or your currency code) at the beginning of the message.\n\n" + \
                                    "Foils: !foil before the cardname will grab a foil version of that card.\n\n" + \
                                    "Prices are taken from www.cardkingdom.com"

                        send_message(sender_id, respond)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    respond = "Type a cardname to get its price!\n\nType !help to see advanced options."
                    send_message(sender_id, respond)
                    

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ.get("PAGE_ACCESS_TOKEN")
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug=True)