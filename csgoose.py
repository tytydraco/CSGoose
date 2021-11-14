import random
from numpy.random import choice

# Logs!
DEBUG = True

# Minimum score ratio to be considered a team carry
CARRY_THRESH_RATIO = 1/4

# Weight towards picking worst player versus the bot frag player
PICK_WORST_PLAYER_WEIGHT = 1/3

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
    Player("Tyler N", 52, 1),
    Player("Tyler C", 41, 0),
    Player("Strafe", 40, 8),
    Player("Eric", 46, 1),
    Player("Ethan", 59, 0),
]

def find_carries(players):
    cumulative_score = sum([p.score for p in players])
    min_carry_score = cumulative_score * CARRY_THRESH_RATIO
    
    debug(f'cumulative score: {cumulative_score}')
    debug(f'min carry score ({CARRY_THRESH_RATIO * 100}th pctl.): {min_carry_score}')

    carries = [p for p in players if p.score > min_carry_score]
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
    print(worst.name)

    bot_frag = pick_inv_bot_frag(players)
    print(bot_frag.name)

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
    
    distri = {}
    total = 0
    for key in l.keys():
        total += l[key]
    for key in l.keys():
        distri[key] = l[key]/total * 100
    
    print(l)
    print(distri)

def main():
    boot_player = pick_boot_player()
    print(f'booted player: {boot_player.name}')

#main()
test_run(1000)