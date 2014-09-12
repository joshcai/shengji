import random

class Card(object):

  C = 'clubs'
  D = 'diamonds'
  H = 'hearts'
  S = 'spades'
  J = 'joker'
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
    17: 'small',
    18: 'big'
  }

  def __str__(self):
    return self.NUM[self.num] + " " + self.suit

  def __init__(self, num, suit):
    self.num = num
    self.suit = suit
    self.trump = False

class Deck(object):

  def __str__(self):
    return str(self.cards)

  def __init__(self, decks=2):
    cards = [Card(x,y) for x in range(2, 15) for y in Card.SUITS]
    cards.append(Card(17, Card.J))
    cards.append(Card(18, Card.J))

    self.cards = decks * cards
    self.shuffle()

    self.size = decks * 54

  def shuffle(self):
    random.shuffle(self.cards)

  def getCards(self):
    current = 0
    while current < self.size:
      yield self.cards[current]
      current += 1

class Hand(object):

  def __str__(self):
    return str([str(x) for x in self.cards])

  def __init__(self):
    self.cards = []

  def addCard(self, card):
    self.cards.append(card)

class Player(object):

  def __init__(self):
    self.hand = Hand()


d = Deck()
p = [Player() for i in range(4)]
print Card.NUM
for i, card in enumerate(d.getCards()):
  p[i%4].hand.addCard(card)
  print card

print "hi"
# print d

print p[0].hand
print len(p[0].hand.cards)

d.shuffle()


