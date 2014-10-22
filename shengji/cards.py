import json
import random

class Card(object):
  """Representation of a single card."""

  C = 'clubs'
  D = 'diamonds'
  H = 'hearts'
  S = 'spades'
  T = 'trump'
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
    """Returns string representation."""
    a = self.NUM[self.actual_num] + " " + self.actual_suit
    if self.num != self.actual_num or self.suit != self.actual_suit:
      a +=" (" + self.NUM[self.num] + " " + self.suit + ")"
    return a

  def __init__(self, num, suit):
    self.num = num # used to compare order of cards
    self.suit = suit # same as actual_suit unless trump
    self.actual_num = num # actual card number
    self.actual_suit = suit # actual card suit

  def smallerThan(self, suit, other_card):
    """Returns whether other_card is greater.

    Args:
      suit: String, suit of the current trick 
      other_card: Card, other card to compare to

    Returns:
      Boolean, True if other_card is greater
    """
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
    """Convert card to trump if it matches trump suit or trump num.

    Args:
      suit: String, trump suit
      num: Integer, trump number
    """
    if self.suit == suit: # trump suit
      self.suit = self.T 
      if self.num == num: # trump suit, trump num
        self.num = 16
    elif self.num == num: # trump num, not trump suit
      self.suit = self.T
      self.num = 15

  def objRepr(self):
    """Return dictionary of attributes for converting to JSON."""
    temp_card = {
        'suit': self.suit, 
        'num': self.num, 
        'actual_suit': self.actual_suit, 
        'actual_num': self.actual_num
    }
    return temp_card

  def convertToJson(self):
    """Returns card in JSON form."""
    return json.dumps(self.objRepr(), separators=(',', ':'))

class Deck(object):

  def __str__(self):
    return str(self.cards)

  def __init__(self, decks=2):
    cards = [Card(x,y) for x in range(2, 15) for y in Card.SUITS]
    cards.append(Card(17, Card.T)) # small joker
    cards.append(Card(18, Card.T)) # big joker

    self.cards = int(decks) * cards

    self.size = decks * 54
    self.current = 0 # used when dealing cards

  def shuffle(self):
    """Shuffle cards, reset position to 0 for dealing."""
    random.shuffle(self.cards)
    self.current = 0

  def getNextCard(self):
    """Gets next card in the deck, return None if no more left."""
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

  def append(self, card):
    self.cards.append(card)

  def convertToJson(self):
    """Returns entire array in JSON form."""
    temp_cards = [card.objRepr() for card in self.cards]
    return json.dumps(temp_cards, separators=(',', ':'))

  def points(self):
    """Counts number of points in the cards."""
    p = 0
    for card in self.cards:
      if card.actual_num == 5:
        p += 5
      elif card.actual_num == 10 or card.actual_num == 13: # ten or kings
        p += 10
    return p

  def __contains__(self, key):
    """Checks to see if a card is in these cards.

    Args:
      key: tuple holding num, suit, and number of times to check (default 1)
    """
    if len(key) == 3:
      num, suit, times = key
    elif len(key) == 2:
      num, suit = key
      times = 1
    else:
      raise Exception('Wrong number of arguments in tuple')

    count = 0
    for card in self.cards:
      if card.suit == suit and card.num == num:
        count += 1
      if count == times:
        return True
    return False

class Hand(Cards):

  def __init__(self):
    super(Hand, self).__init__()

  def removeCard(self, position):
    """Removes and returns card at a certain position.

    Args:
      position: Integer, position of the card to be removed.
    """
    return self.cards.pop(position)

  def empty(self):
    """Returns True if hand is empty."""
    return len(self.cards) == 0

  def trumpify(self, suit, num):
    """Trumpify all cards in the hand.

    Args:
      suit: String, trump suit
      num: Integer, trump num
    """
    for card in self.cards:
      card.trumpify(suit, num)

  def sort(self):
    """Sort cards by suit first, then by number.

    Note: should be called after hand has been trumpified.
    """
    self.cards = sorted(self.cards, key=lambda x: (x.suit, x.num))

  def containsSuit(self, suit):
    """Check if hand has any cards left of a certain suit.

    Args:
      suit: String, suit to check
    """
    for card in self.cards:
      if card.suit == suit:
        return True
    return False

class Trick(Cards):

  @property
  def suit(self):
    """Suit of the trick (equal to the suit of the first card in the trick)."""
    return self.cards[0].suit

  def __init__(self):
    super(Trick, self).__init__()

  def biggest(self):
    """Returns position of the biggest card in the trick."""
    biggestCard = self.cards[0]
    biggestPosition = 0
    for i, card in enumerate(self.cards[1:]):
      if biggestCard.smallerThan(self.suit, card):
        biggestCard = card
        biggestPosition = i + 1
    return biggestPosition