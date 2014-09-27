import json
import random

class Card(object):

  C = 'clubs'
  D = 'diamonds'
  H = 'hearts'
  S = 'spades'
  T  = 'trump'
  SUITS = (C, D, H, S)

  NUM = {
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    11: 'jack',
    12: 'queen',
    13: 'king',
    14: 'ace',
    15: 'trump number',
    16: 'trump number trump suit',
    17: 'small joker',
    18: 'big joker'
  }


  def __str__(self):
    a = self.NUM[self.actual_num] + " " + self.actual_suit
    if self.num != self.actual_num or self.suit != self.actual_suit:
      a +=" (" + self.NUM[self.num] + " " + self.suit + ")"
    return a

  def __init__(self, num, suit):
    self.num = num
    self.suit = suit
    self.actual_num = num
    self.actual_suit = suit

  def smallerThan(self, suit, other_card):
    # print ('comparing ' + str(self) + ' and ' + str(other_card))
    if suit == self.T or self.suit == other_card.suit:
      return other_card.num > self.num
    if self.suit == self.T and other_card.suit != self.T:
      return False
    if self.suit != self.T and other_card.suit == self.T:
      return True
    if self.suit == suit and other_card.suit != suit:
      return False
    if self.suit != suit and other_card.suit == suit:
      return True
    raise Exception('Could not compare cards')

  def trumpify(self, suit, num):
    if self.suit == suit:
      self.suit = self.T
      if self.num == num:
        self.num = 16
    elif self.num == num:
      self.suit = self.T
      self.num = 15

class Deck(object):

  def __str__(self):
    return str(self.cards)

  def __init__(self, decks=2):
    cards = [Card(x,y) for x in range(2, 15) for y in Card.SUITS]
    cards.append(Card(17, Card.T))
    cards.append(Card(18, Card.T))

    self.cards = int(decks) * cards

    self.size = decks * 54
    self.current = 0

  def shuffle(self):
    random.shuffle(self.cards)
    self.current = 0

  def getNextCard(self):
    if self.current < self.size:
      self.current += 1
      return self.cards[self.current-1]
    return None

class Cards(object):

  def __str__(self):
    return str([str(x) for x in self.cards])

  def __init__(self):
    self.cards = []

  def __getitem__(self, index):
    return self.cards[index]

  def addCard(self, card):
    self.cards.append(card)

  def convertToJson(self):
    temp_cards = [{'suit': card.suit, 'num': card.num, 'actual_suit': card.actual_suit, 'actual_num': card.actual_num} for card in self.cards]
    return json.dumps(temp_cards, separators=(',', ':'))

  def points(self):
    p = 0
    for card in self.cards:
      if card.actual_num == 5:
        p += 5
      elif card.actual_num == 10 or card.actual_num == 13: # ten or kings
        p += 10
    return p

class Hand(Cards):

  def __init__(self):
    super(Hand, self).__init__()

  def removeCard(self, position):
    return self.cards.pop(position)

  def empty(self):
    return len(self.cards) == 0

  def trumpify(self, suit, num):
    for card in self.cards:
      card.trumpify(suit, num)

  def sort(self):
    self.cards = sorted(self.cards, key=lambda x: (x.suit, x.num))

  def containsSuit(self, suit):
    for card in self.cards:
      if card.suit == suit:
        return True
    return False

class Trick(Cards):

  @property
  def suit(self):
    return self.cards[0].suit

  def __init__(self):
    super(Trick, self).__init__()

  def biggest(self):
    biggestCard = self.cards[0]
    biggestPosition = 0
    for i, card in enumerate(self.cards[1:]):
      if biggestCard.smallerThan(self.suit, card):
        biggestCard = card
        biggestPosition = i + 1
    return biggestPosition