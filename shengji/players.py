import cards

class Player(object):

  def __init__(self, name="Default", ws=None):
    self.name = name
    self.ws = ws
    self.hand = cards.Hand()
    self.played = False

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