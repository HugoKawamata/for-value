import os
import sys
from ForValue.app import app
import unittest
import tempfile
import json
import ast

class ForValueTestCase(unittest.TestCase):
  def setUp(self):
    app.testing = True
    self.app = app.test_client()


  def tearDown(self):
    return

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
    self.assertEqual("Cancel", ast.literal_eval((response.data).decode("utf-8"))["deets"][0]["name"])
    self.assertEqual("AUD", ast.literal_eval((response.data).decode("utf-8"))["currency"])

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
    self.assertEqual("Cancel", ast.literal_eval((response.data).decode("utf-8"))["deets"][0]["name"])
    self.assertEqual("USD", ast.literal_eval((response.data).decode("utf-8"))["currency"])

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
    self.assertEqual("error", ast.literal_eval((response.data).decode("utf-8"))["deets"][0]["name"])

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
    self.assertEqual("Cancel", ast.literal_eval((response.data).decode("utf-8"))["deets"][0]["name"])
    self.assertEqual("Counterspell", ast.literal_eval((response.data).decode("utf-8"))["deets"][1]["name"])

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
    self.assertEqual("FOIL Cancel", ast.literal_eval((response.data).decode("utf-8"))["deets"][0]["name"])
    
if __name__ == "__main__":
  unittest.main()