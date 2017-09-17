import os
import sys
from models import *
from app import app
import unittest
import tempfile
import json
import ast

def remove_price(reply):
  splitReply = reply.split("\n")
  for cardReply in splitReply:
    splitCardReply = cardReply.split(" ")
    if represents_float(splitCardReply[-1]):
      reply = reply.replace(" " + splitCardReply[-1], "")
  return reply

class ForValueTestCase(unittest.TestCase):
  def setUp(self):
    app.testing = True
    self.app = app.test_client()

  def tearDown(self):
    return

  def test_determine_mode_help(self):
    self.assertEqual("help-mode", determine_mode("!help"))

  def test_determine_mode_cards(self):
    self.assertEqual("price-set-mode", determine_mode("help"))

  def test_reply_one_card(self):
    self.assertEqual(
      "Cancel - 10th Edition (C): USD\n",
      remove_price(compose_message("cancel"))
    )

  def test_one_invalid(self):
    self.assertEqual("No cards were found for that search. Please ensure spelling is correct, and try again. Type !help for help.",\
      compose_message("invalid message"))

  def test_two_cardnames(self):
    self.assertEqual(
      "Cancel - 10th Edition (C): USD\nCounterspell - 3rd Edition (U): USD\nTotal Price:\n",
      remove_price(compose_message("cancel\ncounterspell"))
    )

  def test_foil_cardname(self):
    self.assertEqual(
      "FOIL Cancel - 10th Edition (C): USD\n",
      remove_price(compose_message("!foil cancel"))
    )

  def test_quote_cardname(self):
    self.assertEqual(
      "Shock - 10th Edition (C): USD\n",
      remove_price(compose_message("\"shock\""))
    )

  def test_ignore_currency(self):
    self.assertEqual(
      "Cancel - 10th Edition (C): USD\n",
      remove_price(compose_message("!usd cancel"))
    )
  
  def test_permutations(self):
    self.assertEqual(
      "4 FOIL Cancel - Khans of Tarkir (C): USD\n",
      remove_price(compose_message("4 !foil !ktk Cancel"))
    )

    self.assertEqual(
      "4 FOIL Cancel - Khans of Tarkir (C): USD\n",
      remove_price(compose_message("4 !ktk !foil Cancel"))
    )
  
    
if __name__ == "__main__":
  unittest.main()