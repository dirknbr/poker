
# from __future__ import super_function
# from builtins import super
from estimate import *
import inspect

BET = 1
BUDGET = 100

def prints(hand):
  print(sorted(hand))

# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class Bot:
  def __init__(self, name='', budget=BUDGET):
    self.budget = budget
    self.hand = []
    # self.ingame = True
    self.wins = 0
    self.games = 0
    self.name = name
    self.bet_game = 0
    # just for prob bot: allow p to be adapted later
    self.p1 = .2
    self.p2 = .4
    self.p3 = .6
  def win_rate(self):
    return float(self.wins) / self.games
  def fold(self):
    # self.games += 1
    # self.ingame = False
    self.hand = []
    self.bet_game = 0
  def bet(self, bet=1):
    assert bet <= self.budget, 'not enough budget'
    self.budget -= bet
    self.bet_game += bet
  def win(self, totalpot):
    self.wins += 1
    self.budget += totalpot

# https://www.w3schools.com/python/python_inheritance.asp
class RandomBot(Bot):
  def play(self):
    # check, bet, fold
    if BET <= self.budget:
      return np.random.choice(['check', ['bet', BET], 'fold'], 1, p=[.45, .45, .1])[0]
    else:
      return np.random.choice(['check', 'fold'], 1, p=[.9, .1])[0]

class ProbBot(Bot):
  def play(self, opencards, opps=2):
    assert self.p1 < self.p2
    pwin = estimate(self.hand, opencards, opps=opps, sim=300)
    print(pwin)
    # make p1 and p2 proportional to number of players
    # odds = bet_game / totalpot
    if pwin > self.p3 and BET * 2 <= self.budget:
      return 'bet', BET * 2
    if pwin > self.p2 and BET <= self.budget:
      return 'bet', BET
    elif pwin > self.p1:
      return 'check'
    else:
      return 'fold'

class SimpleBot(Bot):
  def play(self, opencards):
    # if current hand is good proceed
    val = best_hand(self.hand + opencards) 
    if val >= 18:
      return 'bet', 2 * BET
    elif val >= 16:
      return 'bet', BET
    elif val >= 15:
      return 'check'
    else:
      return 'fold'

class Human(Bot):
  def play(self):
    print(bcolors.OKGREEN + 'your cards' + bcolors.ENDC)
    prints(self.hand)
    inp = raw_input('c(check), b(et) or f(old): ')
    if inp == 'c':
      return 'check'
    elif inp == 'b' and BET <= self.budget:
      return 'bet', BET
    elif inp == 'b':
      print('you dont have enough money', self.budget)
    elif inp == 'f':
      return 'fold'


class Game:
  def __init__(self):
    self.totalpot = 0
    self.opencards = []
    # self.bet = 1
    self.players = []
  def remove_player(self, player):
    self.players.remove(player)
  def max_bet(self):
    # return the max bet per player
    return max([p.bet_game for p in self.players])
  def determine_winner(self):
    if len(self.players) > 1:
      vals = [best_hand(p.hand + self.opencards) for p in self.players]
      maxval = max(vals)
      if vals.count(maxval) > 1:
        print(bcolors.BOLD + 'draw no winner' + bcolors.ENDC)
        # people share the pot, find all winners
        winners = [self.players[i] for i in range(len(vals)) if vals[i] == maxval]
        share = float(self.totalpot) / len(winners)
        for p in winners:
          p.budget += share
        print([w.name for w in winners])
        print('shared pot', share)
      else:
        winner = self.players[vals.index(maxval)]
        print(bcolors.BOLD + winner.name + ' has won with ' + str(maxval) + bcolors.ENDC)
        print('the pot is', self.totalpot)
        winner.win(self.totalpot)
      for i, p in enumerate(self.players):
        print(p.name, vals[i])
        prints(p.hand)
    else:
      winner = self.players[0]
      print(bcolors.BOLD + 'one player left ' + winner.name + ' has won' + bcolors.ENDC)
      print('the pot is', self.totalpot)
      winner.win(self.totalpot)
    # reset
    for p in self.players:
      p.fold()



# start the agents
rbot = RandomBot(name='rbot')
rbot2 = RandomBot(name='rbot2')
hum = Human(name='human')
pbot = ProbBot(name='pbot')
pbot2 = ProbBot(name='pbot2')
sbot = SimpleBot(name='sbot')
sbot2 = SimpleBot(name='sbot2')


for roundd in range(5):

  # initialise 1 game
  game = Game()
  game.players = [rbot, rbot2, pbot, pbot2, sbot, sbot2, hum]
  rbot.hand, pile = draw_card(2, PILE)
  rbot2.hand, pile = draw_card(2, pile)
  hum.hand, pile = draw_card(2, pile)
  pbot.hand, pile = draw_card(2, pile)
  pbot2.hand, pile = draw_card(2, pile)
  sbot.hand, pile = draw_card(2, pile)
  for p in game.players:
    p.games += 1
  game.opencards, pile = draw_card(3, pile)

  print('========================================')
  print('round', roundd)
  print('open cards')
  prints(game.opencards)

  # players = game.players[:]

  for step in range(3):
    for p in game.players[:]:
      args = inspect.getargspec(p.play).args
      if len(args) == 3: 
        act = p.play(game.opencards, len(game.players) - 1)
      elif len(args) == 2:
        act = p.play(game.opencards)      
      else:
        act = p.play()
      print(p.name, act)
      if act == 'fold':
        game.remove_player(p)
        p.fold()
      elif act[0] == 'bet':
        bet = act[1]
        p.bet(bet)
        game.totalpot += bet
      else:
        # check, but have to match bettings
        if p.bet_game < game.max_bet():
          diff = game.max_bet() - p.bet_game
          p.bet(diff)
          game.totalpot += diff
    if len(game.opencards) < 5:
      newcard, pile = draw_card(1, pile)
      game.opencards += newcard
    print('open cards')
    prints(game.opencards)  

  game.determine_winner()

for p in [rbot, rbot2, sbot, sbot2, pbot, pbot2, hum]:
  print(p.name, p.budget, p.win_rate())