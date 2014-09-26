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

class Players(object):

  def __init__(self):
    self.players = []

  def __len__(self):
    return len(self.players)

  def __iter__(self):
    self.a = 0
    return self

  def __next__(self):
    if self.a >= len(self.players):
      raise StopIteration
    result = self.players[self.a]
    self.a += 1
    return result

  def add(self, player):
    self.players.append(player)

  def sendMessage(self, message):
    for player in self.players:
      player.sendMessage(message)

  def at(self, num):
    return self.players[num]

class Round(object):

  def __init__(self, game, trump_num, defenders, bottom_player):
    self.game = game
    self.deck = game.deck
    self.players = game.players
    self.num_players = len(self.players)
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
    pass

  @tornado.gen.coroutine
  def declare(self):
    p = yield self.messages.get() # number of player
    for player in self.players:
      player.sendMessage(p + ' has declared')
    return int(p)

  @tornado.gen.coroutine
  def deal(self):
    self.deck.shuffle()
    for i in range(int(self.deck.size - self.bottom_size)):
      card = self.deck.getNextCard()
      self.players.at(i%4).hand.addCard(card)
      self.players.at(i%4).sendMessage(str(card))
      yield tornado.gen.Task(IOLoop.instance().add_timeout, time.time() + .25)
    for i in range(self.bottom_size):
      self.bottom.addCard(self.deck.getNextCard())
    print('DONE DEALING')

  @tornado.gen.coroutine
  def start(self):
    _, declarer = yield [self.deal(), self.declare()]
    print('DONE DEALING + DECLARING')
    if self.defenders == -1:
      self.bottom_player = declarer - 1
      self.defenders = (declarer - 1) % 2
      self.attackers = declarer % 2
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
    while not self.players.at(0).hand.empty():
      print('   Player ' + str(start_player) + ' starting')
      t = cards.Trick()
      for i in range(self.num_players):
        message = yield self.players.at(i%4).ws.q.get()
        t.addCard(self.players.at((i+start_player)%4).hand.removeCard(0))
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
    return (self.attackers, 3, self.bottom_player)

class Game(object):

  def __init__(self):
    self.num_players = 0
    self.players = Players()
    self.deck = cards.Deck(2)
    self.round_scores = [2, 2]
    self.messages = None

  def addPlayer(self, name="No name", ws=None):
    self.players.add(Player(name, ws))
    self.num_players += 1

  # TODO: remove player function

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
      input('   weeeeeeeeeeeee')


if __name__ == "__main__":
  g = Game(4)
  g.addPlayer(name="1")
  g.addPlayer(name="2")
  g.addPlayer(name="3")
  g.addPlayer(name="4")
  g.start()