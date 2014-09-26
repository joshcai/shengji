import game

import tornado.ioloop
import tornado.web
import tornado.websocket
import toro


g = game.Game()

class WSHandler(tornado.websocket.WebSocketHandler):

  name = None

  def check_origin(self, origin):
    return True

  def open(self):
    print("WebSocket opened")
    self.q = toro.Queue(maxsize=1)

  def on_message(self, message):
    print(message)
    m = message.split(' ')
    if m[0] == 'ready':
      self.name = m[1]
      g.addPlayer(m[1], self)
      g.players.sendMessage(m[1] + ' has joined')
      self.write_message('assign ' + str(g.num_players))
      self.write_message('You are player: ' + str(g.num_players))
    elif m[0] == 'start':
      g.messages = toro.Queue(maxsize=4)
      g.start()
    elif m[0] == 'message':
      self.q.put(m[1])
    elif m[0] == 'declare':
      g.messages.put(m[1])

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


