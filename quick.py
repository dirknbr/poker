
# given a hand estimate the prob

from estimate import *

# hearts, spades, clubs, diamonds

myhand = ['H10', 'CA']
opencards = ['H7', 'D7', 'SJ']
opps = 2

def short2long(cards):
  # translate into long form
  dics = {'H': 'Hearts', 'C': 'Clubs', 'D': 'Diamonds', 'S': 'Spades'}
  dicr = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
  for i in range(2, 11):
  	dicr[str(i)] = i
  cards2 = []
  for c in cards:
  	suit = dics[c[0]]
  	rank = dicr[c[1:]]
  	cards2.append((rank, str(rank), suit))
  return cards2

print(short2long(myhand))
print(estimate(short2long(myhand), short2long(opencards), opps=2))
