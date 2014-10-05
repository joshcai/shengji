import unittest
import shengji.cards as cards

class TestCards(unittest.TestCase):

  def testContainsCard(self):
    c = cards.Cards()
    c.append(cards.Card(4, 'hearts'))
    c.append(cards.Card(8, 'hearts'))
    c.append(cards.Card(8, 'spades'))
    self.assertTrue((4, 'hearts') in c)
    self.assertTrue((8, 'hearts') in c)
    self.assertTrue((8, 'spades') in c)
    self.assertFalse((8, 'diamonds') in c)
    self.assertFalse((5, 'clubs') in c)

  def testContainsCardMultiple(self):
    c = cards.Cards()
    c.append(cards.Card(4, 'hearts'))
    c.append(cards.Card(4, 'hearts'))
    self.assertTrue((4, 'hearts') in c)
    self.assertTrue((4, 'hearts', 1) in c)
    self.assertTrue((4, 'hearts', 2) in c)
    self.assertFalse((4, 'hearts', 3) in c)
    self.assertFalse((4, 'hearts', 4) in c)

  def testContainsCardRaiseException(self):
    with self.assertRaises(Exception):
      c = cards.CardS()
      c.append(cards.Card(4, 'hearts'))
      c.append(cards.Card(4, 'hearts'))
      (4) in c

  def testPoints(self):
    c = cards.Cards()
    c.append(cards.Card(5, 'hearts'))
    c.append(cards.Card(10, 'hearts'))
    c.append(cards.Card(13, 'spades')) 
    c.append(cards.Card(7, 'spades')) 
    self.assertEqual(25, c.points())

if __name__ == '__main__':
  unittest.main()