from shengji import game

import tornado.ioloop
import tornado.web
import tornado.websocket
import toro

g = game.Game()

class WSHandler(tornado.websocket.WebSocketHandler):

  name = None

  def check_origin(self, origin):
    # Currently accepts all origins, since this is being hosted on port 7000, 
    # and the client page is beingserved on some other portTODO: Restrict to 
    # certain domain
    return True

  def open(self):
    print("WebSocket opened")
    self.clientMessages = toro.Queue(maxsize=5)

  def on_message(self, message):
    print(message)
    m = message.split(' ')
    if m[0] == 'ready':
      self.name = m[1]
      g.players.add(m[1], self)
      self.num_player = g.num_players # 0 based player id
      g.num_players += 1
      g.players.sendMessage(m[1] + ' has joined')
      self.write_message('assign ' + str(g.num_players))
      self.write_message('You are player: ' + str(g.num_players))
    elif m[0] == 'start':
      g.messages = toro.Queue(maxsize=10)
      g.start()
    elif m[0] == 'play':
      if self.num_player not in g.played: # check if player has played before
        self.clientMessages.put(m[1])
      else:
        self.write_message('Please wait your turn!')
    elif m[0] == 'declare':
      # m[1] is player num, m[2] is suit
      g.messages.put(m[1] + ' ' + m[2])
    elif m[0] == 'bottomExchange':
      bottom = set(m[1].split(','))
      # TODO: check none are out of bounds
      if len(bottom) == 8:
        self.clientMessages.put(m[1])
      else:
        self.write_message('Need 8 unique cards')

    self.write_message(u"You said: " + message)

  def on_close(self):
    # g.broadcast(self.name + " has left")
    print("WebSocket closed")


app = tornado.web.Application([
  (r"/ws", WSHandler),
])

if __name__ == "__main__":
  print("Listening on port 7000")
  app.listen(7000)
  tornado.ioloop.IOLoop.instance().start()


