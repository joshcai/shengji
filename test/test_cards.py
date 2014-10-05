import unittest
import shengji.cards as cards

class TestCards(unittest.TestCase):

  def testCardInit(self):
    c = cards.Card(4, 'hearts')
    self.assertEqual(c.suit, 'hearts')

if __name__ == '__main__':
  unittest.main()