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
    17: 'small',
    18: 'big'
  }

  def __str__(self):
    return self.NUM[self.num] + " " + self.suit

  def __init__(self, num, suit):
    self.num = num
    self.suit = suit
    self.actual_num = num

  def smallerThan(self, suit, other_card):
    # if suit == T or self.suit == other_card.suit:
    #   return other_card if other_card.num > self.num else self
    # if self.suit == T and other_card.suit != T:
    #   return self
    # if self.suit != T and other_card.suit == T:
    #   return other_card
    # if self.suit == suit and other_card.suit != suit:
    #   return self
    # if self.suit != suit and other_card.suit == suit:
    #   return other_card
    print ('comparing ' + str(self) + ' and ' + str(other_card))
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


class Deck(object):

  def __str__(self):
    return str(self.cards)

  def __init__(self, decks=2):
    cards = [Card(x,y) for x in range(2, 15) for y in Card.SUITS]
    cards.append(Card(17, Card.T))
    cards.append(Card(18, Card.T))

    self.cards = int(decks) * cards
    self.shuffle()

    self.size = decks * 54
    self.current = 0

  def shuffle(self):
    random.shuffle(self.cards)

  # def getCards(self):
  #   current = 0
  #   while current < self.size:
  #     yield self.cards[current]
  #     current += 1

  def getNextCard(self):
    if self.current < self.size:
      self.current += 1
      return self.cards[self.current-1]
    return None

class Hand(object):

  def __str__(self):
    return str([str(x) for x in self.cards])

  def __init__(self):
    self.cards = []

  def addCard(self, card):
    self.cards.append(card)

  def removeCard(self, position):
    return self.cards.pop(position)

  def empty(self):
    return len(self.cards) == 0

class Player(object):

  def __init__(self):
    self.hand = Hand()

class Trick(object):

  @property
  def suit(self):
    return self.cards[0].suit

  def __init__(self):
    self.cards = []

  def addCard(self, card):
    self.cards.append(card)
    print(card)

  def biggest(self):
    biggestCard = self.cards[0]
    biggestPosition = -1
    for i, card in enumerate(self.cards[1:]):
      if biggestCard.smallerThan(self.suit, card):
        biggestCard = card
        biggestPosition = i
    return biggestPosition+1

class Game(object):

  def __init__(self, num_players):
    self.num_players = num_players
    self.players = [Player() for i in range(num_players)]
    self.deck = Deck(num_players / 2)
    # fix later
    self.bottom_size = 8
    self.bottom = []

  def start(self):
    self.deal()
    # fix later
    self.trump = Card.SUITS[random.randint(0,3)]
    print('Trump Suit is ' + self.trump)
    self.bottomExchange()
    self.tricks = []
    start_player = 0
    while not self.players[0].hand.empty():
      print('Player ' + str(start_player) + ' starting')
      t = Trick()
      for i in range(self.num_players):
        t.addCard(self.players[(i+start_player)%4].hand.removeCard(0))
      start_player = t.biggest()
      print('Player ' + str(start_player) + ' won')
      self.tricks.append(t)
      # raw_input("              continue...")

  def bottomExchange(self):
    pass

  def deal(self):
    for i in range(int(self.deck.size - self.bottom_size)):
      self.players[i%4].hand.addCard(self.deck.getNextCard())
    for i in range(self.bottom_size):
      self.bottom.append(self.deck.getNextCard())

    # for i, card in enumerate(d.getCards()):
      # self.players[i%4].hand.addCard(card)

game = Game(4)
game.start()



