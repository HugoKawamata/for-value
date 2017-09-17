import os
import sys
from models import *
from app import app
import unittest
import tempfile
import json
import ast

class ForValueTestCase(unittest.TestCase):
  def setUp(self):
    app.testing = True
    self.app = app.test_client()

  def remove_price(self, reply):
    splitReply = reply.split(" ")
    if represents_float(splitReply[-1]):
      reply.replace(" " + splitReply[-1], "")
    return reply

  def tearDown(self):
    return

  def test_determine_mode_help(self):
    self.assertEqual("help-mode", determine_mode("!help"))

  def test_determine_mode_cards(self):
    self.assertEqual("price-set-mode", determine_mode("help"))

  def test_reply_one_card(self):
    self.assertEqual(
      "Cancel - 10th Edition (C): AUD"
      remove_price(compose_message("cancel"))
    )

  def test_to_search_list_two_cards(self):
    self.assertEqual(
      [{"search": "cancel", "quantity": 1},
      {"search": "counterspell", "quantity": 1}],
      message_to_search_list("cancel\ncounterspell")
    )

  def test_to_search_list_foil(self):
    self.assertEqual(
      [{"search": "cancel&filter[tab]=mtg_foil", "quantity": 1}],
      message_to_search_list("!foil cancel")
    )

  def test_to_search_list_complex_1(self):
    self.assertEqual(
      [{"search": "ach%21+hans%2C+run%21", "quantity": 1}],
      message_to_search_list("ach! hans, run!")
    )

  def test_to_search_list_complex_2(self):
    self.assertEqual(
      [{"search": "look+at+me%2C+i%27m+r%26d", "quantity": 1}],
      message_to_search_list("look at me, i'm r&d")
    )

  def test_to_currency_alt_currency(self):
    message = "!USD cancel"
    self.assertEqual(
      {"currency": "USD", "message": "cancel"},
      message_to_currency_and_message(message)
    )

  def test_compose_invalid_card(self):
    self.assertEqual(
      "No cards were found for that search. Please ensure spelling is correct, and try again. Type !help for help.",
      compose_message("jfejfijiej")
    )

  def test_compose_invalid_cards(self):
    self.assertEqual(
      "No cards were found for those searches. Please ensure spelling is correct, and try again. Type !help for help.",
      compose_message("uhdehwifh\n hduewhdiuhw")
    )

  def test_one_cardname(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "cancel", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    reply = response.data.decode("utf-8")
    self.assertEqual(True, "Cancel" in reply)
    self.assertEqual(True, "AUD" in reply)

  def test_one_cardname_and_currency(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "!usd cancel", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    reply = response.data.decode("utf-8")
    self.assertEqual(True, "Cancel" in reply)
    self.assertEqual(True, "USD" in reply)

  def test_help(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "!help", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    helpMsg = "You can type cardnames on multiple lines in the same message to get a price sum.\n\n" + \
            "Currency Conversion: !USD (or your currency code) at the beginning of the message.\n\n" + \
            "Foils: !foil before the cardname will grab a foil version of that card.\n\n" + \
            "Prices are taken from www.cardkingdom.com"

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    self.assertEqual(helpMsg, response.data.decode("utf-8"))

  def test_one_invalid(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "my name is jeff", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    self.assertEqual("No cards were found for that search. Please ensure spelling is correct, and try again. Type !help for help.",\
      response.data.decode("utf-8"))

  def test_two_cardnames(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "cancel\ncounterspell", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    reply = response.data.decode("utf-8")
    self.assertEqual(True, "Cancel " in reply)
    self.assertEqual(True, "Counterspell " in reply)

  def test_foil_cardname(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "!foil cancel", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    reply = response.data.decode("utf-8")
    self.assertEqual(True, "FOIL Cancel " in reply)

  def test_quote_cardname(self):
    msg = {
      'object': 'page', 
      'entry': [
        {
          'id': '105450440150445', 
          'time': 1501717899854, 
          'messaging': [
            {
              'message': {
                'seq': 722634, 
                'text': "\"shock\"", 
                'mid': 'mid.$cAAAFG7VCCedj1qHxX1dpVypPDVTi'
              }, 
              'sender': {
                'id': '1528753840478227'
              }, 
              'recipient': {
                'id': '105450440150445'
              }, 
              'timestamp': 1501717899615
            }
          ]
        }
      ]
    }

    jsonMsg = json.dumps(msg)

    response = self.app.post("/", data=jsonMsg, content_type="application/json")
    reply = response.data.decode("utf-8")
    self.assertEqual(True, "Shock " in reply)

    
if __name__ == "__main__":
  unittest.main()