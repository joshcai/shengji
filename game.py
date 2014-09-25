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

class Round(object):

  def __init__(self, deck, players, trump_num, defenders):
    self.deck = deck
    self.players = players
    self.num_players = len(players)
    self.bottom = cards.Hand()
    self.trump_num = trump_num
    self.defenders = defenders # 0 for even, 1 for odd, -1 for first round
    self.attackers = (defenders + 1) % 2
    self.score = 0
    self.bottom_size = 8

  @tornado.gen.coroutine
  def bottomExchange(self):
    pass

  @tornado.gen.coroutine
  def deal(self):
    self.deck.shuffle()
    for i in range(int(self.deck.size - self.bottom_size)):
      card = self.deck.getNextCard()
      self.players[i%4].hand.addCard(card)
      if self.players[i%4].ws:
        self.players[i%4].sendMessage(str(card))
      yield tornado.gen.Task(IOLoop.instance().add_timeout, time.time() + .01)
    for i in range(self.bottom_size):
      self.bottom.addCard(self.deck.getNextCard())

  @tornado.gen.coroutine
  def start(self):
    yield self.deal()
    print('DONE DEALING')
    # TODO: first round, first to declare is defending
    if self.defenders == -1:
      self.defenders = 0
      self.attackers = 1
    self.trump_suit = cards.Card.SUITS[random.randint(0,3)]
    print('Trump Suit is ' + self.trump_suit)
    self.trump_num = 2
    print('Trump Num is ' + str(self.trump_num))
    for hand in [x.hand for x in self.players] + [self.bottom]:
      hand.trumpify(self.trump_suit, self.trump_num)
      hand.sort()

    yield self.bottomExchange()
    self.tricks = []
    start_player = 0
    while not self.players[0].hand.empty():
      print('   Player ' + str(start_player) + ' starting')
      t = cards.Trick()
      for i in range(self.num_players):
        message = yield self.players[i%4].ws.q.get()
        print('GOT MESSAGE')
        t.addCard(self.players[(i+start_player)%4].hand.removeCard(0))
      start_player = t.biggest()
      print('   Player ' + str(start_player) + ' won')
      if start_player % 2 != self.defenders:
        print('      Points was at ' + str(self.score))
        self.score += t.points()
        print('      Points are now at ' + str(self.score))
      self.tricks.append(t)

    if start_player % 2 != self.defenders:
      print('Points on the bottom: ' + str(self.bottom.points()))
      self.score += 2 * self.bottom.points()

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
    return (self.attackers, 3)

class Game(object):

  def __init__(self):
    self.num_players = 0
    self.players = []
    self.deck = cards.Deck(2)
    self.round_scores = [2, 2]

  def addPlayer(self, name="No name", ws=None):
    self.players.append(Player(name, ws))
    self.num_players += 1

  # TODO: remove player function

  @tornado.gen.coroutine
  def start(self):
    r = Round(self.deck, self.players, 2, -1)
    # print('Winner + jump: ' + str(last_won) + " " + str(jump))
    while True:
      last_won, jump = yield r.start()
      self.round_scores[last_won] += jump
      # TODO: make sure doesn't jump past 5/10/K
      print('Winner + jump: ' + str(last_won) + " " + str(jump))
      print('Score Count: ' + str(last_won) + ' ' + str(self.round_scores))
      if self.round_scores[0] >= 15 or self.round_scores[1] >= 15:
        break
      r = Round(self.deck, self.players, self.round_scores[last_won], last_won)
      input('   weeeeeeeeeeeee')


  def broadcast(self, message):
    for player in self.players:
      player.sendMessage(message)

if __name__ == "__main__":
  g = Game(4)
  g.addPlayer(name="1")
  g.addPlayer(name="2")
  g.addPlayer(name="3")
  g.addPlayer(name="4")
  g.start()