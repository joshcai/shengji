shengji
---
Shengji (also known as 80 Points, and many other names) is a Chinese card game, usually played with 2 decks and 4 players. You can find the [rules on how to play here](http://www.pagat.com/kt5/tractor.html).

There's still lots of pieces missing to this, including:

- allowing doubles to be played
- allowing flushes to be played
- allowing tractors to be played
- support for more than 4 players, and more than 2 decks
- handling disconnects
- graphics are missing (lol it's text-based right now)

This is currently being developed using Python 3.4.1 with the Tornado framework. You can run the game by doing (preferably in a virtualenv):

```shell
pip install -r requirements.txt
python shengji/app.py
```

You'll also want to serve the client, which you can find in the [shengji-client](http://github.com/joshcai/shengji-client) repository.

You can run the tests using:

```shell
python -m unittest discover test
```
