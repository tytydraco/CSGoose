import random
import numpy as np
from numpy.random import choice

# Logs!
DEBUG = True

# Weight towards picking worst player versus the bot frag player
PICK_WORST_PLAYER_WEIGHT = 1/3

# How potent of an outlier to discover during carry picking
CARRY_OUTLIER_RATIO = 1.5

def debug(msg):
    if DEBUG == True:
        print(msg)

class Player:
    bot_frag_prob = 0
    carry = False
    
    def __init__(self, name, score, bot_frag_cnt = 0):
        self.name = name
        self.score = score
        self.bot_frag_cnt = bot_frag_cnt

hardcoded_players = [
    Player("Tyler N",   24,     1),
    Player("Tyler C",   21,     0),
    Player("Strafe",    14,     8),
    Player("Eric",      31,     1),
    Player("Ethan",     46,     0),
]

def make_outlier(players):
    scores = [p.score for p in players]
    third_q = np.quantile(scores, 3/4)
    outlier_score = third_q * CARRY_OUTLIER_RATIO
    debug(f'simulated carry score: {outlier_score}')
    return outlier_score

def find_carries(players):
    outlier_score = make_outlier(players)

    simulated_player = Player("Simulated", outlier_score)
    players.append(simulated_player)

    player_scores = [p.score for p in players]

    avg_simulated_score = np.mean(player_scores)
    std_simulated_score = np.std(player_scores)
    min_carry_score = avg_simulated_score + std_simulated_score

    debug(f'min carry score: {min_carry_score}')

    carries = [p for p in players if p.score >= min_carry_score]
    debug(f'carries: {[p.name for p in carries]}')

    for p in carries:
        p.carry = True
    
    return carries

def pick_worst(players):
    worst_score = min([p.score for p in players])
    worst_players = [p for p in players if p.score == worst_score]
    
    debug(f'worst player(s): {[p.name for p in worst_players]}')

    worst_player = random.choice(worst_players)
    debug(f'worst player: {worst_player.name}')

    return worst_player

def pick_inv_bot_frag(players):
    game_cnt = sum([p.bot_frag_cnt for p in players])
    total_prob = 0

    for p in players:
        prob = 1 - (p.bot_frag_cnt / game_cnt)
        p.bot_frag_prob = prob
        total_prob += prob

    prob_list = []
    for p in players:
        prob = p.bot_frag_prob / total_prob
        prob_list.append(prob)
        debug(f'bot frag choice prob: {p.name}\t{prob}')
    
    boot_player = choice(players, 1, p = prob_list)[0]
    debug(f'bot frag booted player: {boot_player.name}')
    return boot_player

def pick_between_two(worst, bot_frag):
    worst_weight = PICK_WORST_PLAYER_WEIGHT

    player_list = [worst, bot_frag]
    prob_list = [worst_weight, 1 - worst_weight]
    boot_player = choice(player_list, 1, p = prob_list)[0]
    debug(f'weighted boot player: {boot_player.name}')

    return boot_player

def pick_boot_player():
    players = hardcoded_players.copy()
    carries = find_carries(players)

    for carry in carries:
        players.remove(carry)
    
    worst = pick_worst(players)
    bot_frag = pick_inv_bot_frag(players)
    boot_player = pick_between_two(worst, bot_frag)

    return boot_player

def test_run(iters = 1000):
    l = {}
    for _ in range(0, iters):
        boot_player = pick_boot_player()
        name = boot_player.name
        if name not in l.keys():
            l[name] = 0
        l[name] += 1
    
    dist = {}

    total = sum(l.values())
    for key in l.keys():
        dist[key] = l[key]/total * 100
    
    print()
    print('===== Kick Probability =====')
    for p in sorted(dist):
        print(f'{p}\t\t{round(dist[p])}%')

def main():
    boot_player = pick_boot_player()
    print()
    msg = f'    We will miss you {boot_player.name}!    '
    print('=' * (len(msg)))
    print(msg)
    print('=' * (len(msg)))

main()
#test_run(5000)