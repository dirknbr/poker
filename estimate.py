
import numpy as np
from itertools import combinations

cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
cards_val = [i for i in range(2, 15)]
suits = ['Clubs', 'Diamonds', 'Spades', 'Hearts']
# players = 2

PILE = [(i[0], i[1], j) for i in zip(cards_val, cards) for j in suits]

def values(cards):
  return [i[0] for i in cards]

def suitsf(cards):
  return [i[2] for i in cards]

def is_pair(cards):
  for i in range(2, 15):
    if values(cards).count(i) == 2:
      return True
  return False

def is_2_pairs(cards):
  vals = values(cards)
  uniq = list(set(vals))
  counts = sorted([vals.count(i) for i in uniq])
  return counts == [1, 2, 2]

def is_triple(cards):
  for i in range(2, 15):
    if values(cards).count(i) == 3:
      return True
  return False

def is_quad(cards):
  for i in range(2, 15):
    if values(cards).count(i) == 4:
      return True
  return False

def is_fullhouse(cards):
  vals = values(cards)
  uniq = list(set(vals))
  counts = sorted([vals.count(i) for i in uniq])
  return counts == [2, 3]

def is_flush(cards):
  suitss = suitsf(cards)
  return len(set(suitss)) == 1

def is_straight(cards):
  vals = values(cards)
  uniq = list(set(vals))
  return len(uniq) == 5 and max(vals) == min(vals) + 4

def is_straight_flush(cards):
  return is_straight(cards) and is_flush(cards)

def high_card(cards):
  return max(values(cards))

def is_royal_flush(cards):
  return is_straight_flush(cards) and high_card(cards) == 14

def best_hand(cards):
  # given 5 to 7 cards, assign value
  if len(cards) > 5:
    # find all combos
    combos = combinations(cards, 5)
  else:
    combos = [cards]
  best = -1
  for c in combos:
    if is_royal_flush(c):
      val = 23
    elif is_straight_flush(c):
      val = 22
    elif is_quad(c):
      val = 21
    elif is_fullhouse(c):
      val = 20
    elif is_flush(c):
      val = 19
    elif is_straight(c):
      val = 18
    elif is_triple(c):
      val = 17
    elif is_2_pairs(c):
      val = 16
    elif is_pair(c):
      val = 15
    else:
      val = high_card(c)
    best = max([best, val])
  return best

def estimate(cards, opencards, thresh=15, opps=None, sim=500, strict=False):
  # return prob of exceeding x points or simulate opponents
  wins = 0
  pile = remain_pile(PILE, cards + opencards)
  for _ in range(sim):
    newopencards, rempile = draw_card(5 - len(opencards), pile)
    totopencards = opencards + newopencards
    if opps is not None:
      # draw 2 cards for each other player
      oppsbeaten = 0
      for _ in range(opps):
        oppcards, rempile = draw_card(2, rempile)
        if strict:
          if evaluate(cards + totopencards, oppcards + totopencards) > 0:
            oppsbeaten += 1
        else:
          # allow draws
          if evaluate(cards + totopencards, oppcards + totopencards) >= 0:
            oppsbeaten += 1
      if oppsbeaten == opps:
        wins += 1
    else:
      if best_hand(cards + totopencards) >= thresh:
        wins += 1
  return float(wins) / sim


def evaluate(a, b):
  # given 2 hands return which hand wins
  return best_hand(a) - best_hand(b)

def draw_card(n=1, pile=PILE):
  # draw 1+ cards given pile, return also new pile
  idx = list(np.random.choice(len(pile), n, replace=False))
  draw = [pile[i] for i in idx]
  return draw, remain_pile(pile, draw)

def shuffle(cards):
  np.random.shuffle(cards)

def remain_pile(pile, cards):
  return [i for i in pile if i not in cards]

shuffle(PILE)

# handa, rem_pile = draw_card(5, pile)
# print(handa)
# print(best_hand(handa))

# handb, rem_pile = draw_card(5, rem_pile)
# print(handb)
# print(best_hand(handb))

# print(evaluate(handa, handb))

# hand, pile = draw_card(2, PILE)
# opencards, pile = draw_card(4, pile)

# print(hand, opencards)
# print(estimate(hand, opencards, opps=1))