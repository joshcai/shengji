import random
import time

import cards

from tornado.ioloop import IOLoop
import tornado.gen

class Player(object):

  def __init__(self, name="Default", ws=None):
    self.name = name
    self.ws = ws
    self.hand = cards.Hand()

  def sendMessage(self, message):
    self.ws.write_message(message)

  def fromClient(self):
    return self.ws.clientMessages

class Players(object):

  def __init__(self):
    self.players = []

  def __len__(self):
    return len(self.players)

  def __getitem__(self, index):
    return self.players[index]

  def __iter__(self):
    self.a = 0
    return self

  def __next__(self):
    if self.a >= len(self.players):
      raise StopIteration
    result = self.players[self.a]
    self.a += 1
    return result

  def add(self, name, ws):
    self.players.append(Player(name, ws))

  # TODO: removePlayer function

  def sendMessage(self, message):
    for player in self.players:
      player.sendMessage(message)

class Round(object):

  def __init__(self, game, trump_num, defenders, bottom_player):
    self.game = game
    self.deck = game.deck
    self.players = game.players
    self.num_players = len(self.players)
    self.hands = [x.hand for x in self.players]
    self.bottom = cards.Hand()
    self.trump_num = trump_num
    self.defenders = defenders # 0 for even, 1 for odd, -1 for first round
    self.attackers = (defenders + 1) % 2
    self.score = 0
    self.bottom_size = 8 # TODO: fix for different sized decks
    self.bottom_player = bottom_player
    self.messages = game.messages

  @tornado.gen.coroutine
  def bottomExchange(self):
    player = self.players[self.bottom_player]
    hand = self.hands[self.bottom_player]

    player.sendMessage('Exchange bottom now!')
    bottom = yield player.fromClient().get()
    bottom = [int(x) for x in bottom.split(',')]
    for i in sorted(bottom, reverse=True):
      self.bottom.addCard(hand.removeCard(i))
    self.players.sendMessage('Bottom has been swapped out')
    player.sendMessage('cards ' + hand.convertToJson())
    player.sendMessage('Bottom:\n' + str(self.bottom))

  @tornado.gen.coroutine
  def declare(self):
    p, suit = yield self.messages.get() # number of player
    for player in self.players:
      player.sendMessage(p + ' has declared')
    return int(p), suit

  @tornado.gen.coroutine
  def deal(self):
    self.deck.shuffle()
    for i in range(int(self.deck.size - self.bottom_size)):
      card = self.deck.getNextCard()
      self.hands[i%4].addCard(card)
      self.players[i%4].sendMessage(str(card))
      yield tornado.gen.Task(IOLoop.instance().add_timeout, time.time() + .01)
    for i in range(self.bottom_size):
      self.bottom.addCard(self.deck.getNextCard())

  @tornado.gen.coroutine
  def start(self):
    _, (declarer, suit) = yield [self.deal(), self.declare()]
    if self.defenders == -1:
      self.bottom_player = declarer - 1
      self.defenders = (declarer - 1) % 2
      self.attackers = declarer % 2
    self.trump_suit = suit
    self.players.sendMessage('Trump Suit is ' + self.trump_suit)
    self.players.sendMessage('Trump Num is ' + str(self.trump_num))
    while not self.bottom.empty():
      self.hands[self.bottom_player].addCard(self.bottom.removeCard(0))
    for hand in self.hands:
      hand.trumpify(self.trump_suit, self.trump_num)
      hand.sort()
    for player in self.players:
      player.sendMessage('cards ' + player.hand.convertToJson())

    yield self.bottomExchange()
    self.tricks = []
    start_player = self.bottom_player
    while not self.hands[0].empty():
      print('   Player ' + str(start_player) + ' starting')
      t = cards.Trick()
      for i in range(self.num_players):
        turn = (i+start_player) % 4
        self.players[turn].sendMessage('Your turn!')
        while True: # prevent cheating
          cardNum = yield self.players[turn].fromClient().get()
          cardNum = int(cardNum)
          if i == 0 or self.hands[turn][cardNum].suit == t[0].suit or not self.hands[turn].containsSuit(t[0].suit):
            break
          self.players[turn].sendMessage('Illegal move')
        played_card = self.hands[turn].removeCard(cardNum)
        if i == 0:
          self.players.sendMessage('tricktype ' + played_card.suit)
        self.players.sendMessage('Player ' + str(turn) + ' played ' + str(played_card))
        t.addCard(played_card)
      start_player = (t.biggest() + start_player) % 4
      self.players.sendMessage('Player ' + str(start_player) + ' won last trick')
      if start_player % 2 != self.defenders:
        self.score += t.points()
        self.players.sendMessage('score ' + str(self.score))
      self.tricks.append(t)

    if start_player % 2 != self.defenders:
      self.players.sendMessage('Points on the bottom: ' + str(self.bottom.points()))
      self.score += 2 * self.bottom.points()
      self.players.sendMessage('score ' + str(self.score))

    print('Final score ' + str(self.score))

    return self.determineFinal()

  def determineFinal(self):
    a = self.num_players * 10
    if self.score == 0:
      return (self.defenders, 3)
    if self.score > 0 and self.score < a:
      return (self.defenders, 2)
    if self.score >= a and self.score < 2*a:
      return (self.defenders, 1)
    if self.score >= 2*a and self.score < 3*a:
      return (self.attackers, 0)
    if self.score >= 3*a and self.score < 4*a:
      return (self.attackers, 1)
    if self.score >= 4*a and self.score < 5*a:
      return (self.attackers, 2)
    return (self.attackers, 3, self.bottom_player)

class Game(object):

  def __init__(self):
    self.num_players = 0
    self.players = Players()
    self.deck = cards.Deck(2)
    self.round_scores = [2, 2]
    self.messages = None

  @tornado.gen.coroutine
  def start(self):
    r = Round(self, 2, -1, -1)
    # print('Winner + jump: ' + str(last_won) + " " + str(jump))
    while True:
      last_won, jump, bottom_player = yield r.start()
      self.round_scores[last_won] += jump
      if bottom_player % 2 != last_won % 2: # opposing team won
        bottom_player = (bottom_player + 1) % 2
      else:
        bottom_player = (bottom_player + 2) % 2
      # TODO: make sure doesn't jump past 5/10/K
      print('Winner + jump: ' + str(last_won) + " " + str(jump))
      print('Score Count: ' + str(last_won) + ' ' + str(self.round_scores))
      if self.round_scores[0] >= 15 or self.round_scores[1] >= 15:
        break
      r = Round(self, self.round_scores[last_won], last_won, bottom_player)
