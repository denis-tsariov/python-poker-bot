from itertools import combinations, permutations
from collections import Counter
import time
#from types import *
poker_hand_percentiles = {
    "AAo": 0, "AKs": 2, "AQs": 2, "AJs": 3, "ATs": 5, "A9s": 8, "A8s": 10, "A7s": 13, "A6s": 14, "A5s": 12, "A4s": 14, "A3s": 14, "A2s": 17,
    "AKo": 5, "KKo": 1, "KQs": 3, "KJs": 3, "KTs": 6, "K9s": 10, "K8s": 16, "K7s": 19, "K6s": 24, "K5s": 25, "K4s": 25, "K3s": 26, "K2s": 26,
    "AQo": 8, "KQo": 9, "QQo": 1, "QJs": 5, "QTs": 6, "Q9s": 10, "Q8s": 19, "Q7s": 26, "Q6s": 28, "Q5s": 29, "Q4s": 29, "Q3s": 30, "Q2s": 31,
    "AJo": 12, "KJo": 14, "QJo": 15, "JJo": 2, "JTs": 6, "J9s": 11, "J8s": 17, "J7s": 27, "J6s": 33, "J5s": 35, "J4s": 37, "J3s": 37, "J2s": 38,
    "ATo": 18, "KTo": 20, "QTo": 22, "JTo": 21, "TTo": 4, "T9s": 10, "T8s": 16, "T7s": 25, "T6s": 31, "T5s": 40, "T4s": 40, "T3s": 41, "T2s": 41,
    "A9o": 32, "K9o": 35, "Q9o": 36, "J9o": 34, "T9o": 31, "99o": 7, "98s": 17, "97s": 24, "96s": 29, "95s": 38, "94s": 47, "93s": 47, "92s": 49,
    "A8o": 39, "K8o": 50, "Q8o": 53, "J8o": 48, "T8o": 43, "98o": 42, "88o": 9, "87s": 21, "86s": 27, "85s": 33, "84s": 40, "83s": 53, "82s": 54,
    "A7o": 45, "K7o": 57, "Q7o": 66, "J7o": 64, "T7o": 59, "97o": 55, "87o": 52, "77o": 12, "76s": 25, "75s": 28, "74s": 37, "73s": 45, "72s": 56,
    "A6o": 51, "K6o": 60, "Q6o": 71, "J6o": 80, "T6o": 74, "96o": 68, "86o": 61, "76o": 57, "66o": 16, "65s": 27, "64s": 29, "63s": 38, "62s": 49,
    "A5o": 44, "K5o": 63, "Q5o": 75, "J5o": 82, "T5o": 89, "95o": 83, "85o": 73, "75o": 65, "65o": 58, "55o": 20, "54s": 28, "53s": 32, "52s": 39,
    "A4o": 46, "K4o": 67, "Q4o": 76, "J4o": 85, "T4o": 90, "94o": 95, "84o": 88, "74o": 78, "64o": 70, "54o": 62, "44o": 23, "43s": 36, "42s": 41,
    "A3o": 49, "K3o": 67, "Q3o": 77, "J3o": 86, "T3o": 92, "93o": 96, "83o": 98, "73o": 93, "63o": 81, "53o": 72, "43o": 76, "33o": 23, "32s": 46,
    "A2o": 54, "K2o": 69, "Q2o": 79, "J2o": 87, "T2o": 94, "92o": 97, "82o": 99, "72o": 100, "62o": 95, "52o": 84, "42o": 86, "32o": 91, "22o": 24,
}

#each hand must be a sorted list in descending order of card strangth and a list of the corresponding suits of those cards
c_list = ['A', 'Q', 'K', 'J', '3', '4', '3']
def card_strength(c):
    if c == 'A': return -14
    elif c=='K': return -13
    elif c=='Q': return -12
    elif c=='J': return -11
    else: return -int(c)

l = sorted(c_list, key=card_strength)
print(l)

def get_best_hand(cards_list, suits_list):
    most_common_numbers = Counter(cards_list).most_common(len(cards_list))
    print(most_common_numbers)

    #for val in most_common_numbers:


def get_best_poker_hand(cards):
    #start = time.time()
    ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
             '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def is_flush(hand):
        suits = [suit for _, suit in hand]
        return len(set(suits)) == 1
    
    def is_straight(hand):
        sorted_ranks = sorted([ranks[rank] for rank, _ in hand])
        l = list(range(sorted_ranks[0], sorted_ranks[0] + 5))
        return sorted_ranks == l
    
    def get_hand_rank(hand):
        rank_counts = Counter([rank for rank, _ in hand])
        counts = sorted(rank_counts.values(), reverse=True)
        sorted_hand_ranks = sorted([ranks[rank] for rank in rank_counts.keys()], reverse=True)
        
        if is_flush(hand) and is_straight(hand):
            return (9, sorted_hand_ranks) if max(sorted_hand_ranks) == 14 else (8, sorted_hand_ranks)
        if counts == [4, 1]:
            return (7, sorted_hand_ranks)
        if counts == [3, 2]:
            return (6, sorted_hand_ranks)
        if is_flush(hand):
            return (5, sorted_hand_ranks)
        if is_straight(hand):
            return (4, sorted_hand_ranks)
        if counts == [3, 1, 1]:
            return (3, sorted_hand_ranks)
        if counts == [2, 2, 1]:
            return (2, sorted_hand_ranks)
        if counts == [2, 1, 1, 1]:
            return (1, sorted_hand_ranks)
        return (0, sorted_hand_ranks)
    
    best_hand = max(combinations(cards, 5), key=get_hand_rank)
    #end = time.time()
    #print(end-start)
    return best_hand, get_hand_rank(best_hand)

def compare_hands(cards1, cards2):
    best_hand1, rank1 = get_best_poker_hand(cards1)
    best_hand2, rank2 = get_best_poker_hand(cards2)
    print(best_hand1, rank1)
    print(best_hand2, rank2)
    if rank1[0] > rank2[0]:
        return 1
    elif rank2[0] > rank1[0]:
        return -1
    else:
        for i in range(0, len(rank1[1])):
            if rank1[1][i] > rank2[1][i]:
                return 1
            elif rank2[1][i] > rank1[1][i]:
                return -1
    return 0

def parse_hand_string(hand_string):
    suits = ['Heart', 'Diamond', 'Club', 'Spade']
    rank_map = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
                'T': '10', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'}
    
    
    rank1, rank2, suited = hand_string[0], hand_string[1], hand_string[2]
        
    if suited == 's':
        return [[(rank_map[rank1], suit1), (rank_map[rank2], suit1)] for suit1 in suits]
    else:
        if rank_map[rank1] == rank_map[rank2]: return [[(rank_map[rank1], suit1), (rank_map[rank2], suit2)] for suit1, suit2 in combinations(suits, 2)]
        return [[(rank_map[rank1], suit1), (rank_map[rank2], suit2)] for suit1, suit2 in permutations(suits, 2)]
def parse_all_hands(list_hand_string):
    all_hands = []
    for hand in list_hand_string:
        all_hands = all_hands + parse_hand_string(hand)
    return all_hands
# Example usage:
# cards = [('A', 'Diamond'), ('K', 'Diamond'), ('Q', 'Diamond'), ('J', 'Diamond'), ('10', 'Diamond'),
#          ('3', 'Spade'), ('2', 'Heart')]
# cards2 = [('A', 'Spade'), ('K', 'Spade'), ('Q', 'Spade'), ('J', 'Spade'), ('10', 'Spade'),
#           ('5', 'Heart'), ('4', 'Club')]

# result = compare_hands(cards, cards2)
# print(result)
print(parse_hand_string('AQo'))
# # Test parse_hand_string function
# #print(parse_hand_string('AKs'))
# print(len(parse_hand_string('Q2o')))