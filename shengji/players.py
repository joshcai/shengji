import shengji.cards as cards

class Player(object):

  def __init__(self, name="Default", ws=None):
    self.name = name 
    self.ws = ws # WebSockets connection
    self.hand = cards.Hand()
    self.played = False # prevent player from playing twice in one trick

  def sendMessage(self, message):
    """Send message to specific player.

    Args:
      message: String, message to send
    """
    self.ws.write_message(message)

  def fromClient(self):
    """Returns toro queue with client messages.

    To get next message, use .get() 
    """
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
    """Sends message to all players.

    Args:
      message: String, message to send.
    """
    for player in self.players:
      player.sendMessage(message)