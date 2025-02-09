import asyncio
from typing import Tuple
import argparse
import treys
import time
from collections import defaultdict
from tg.bot import Bot
import tg.types as pokerTypes
from . import eval_hand_strength

parser = argparse.ArgumentParser(
    prog="Template bot",
    description="A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)",
)

parser.add_argument("--port", type=int, help="The port to connect to the server on")
parser.add_argument(
    "--host", type=str, default="localhost", help="The host to connect to the server on"
)
parser.add_argument(
    "--room", type=str, default="my-new-room", help="The room to connect to"
)
parser.add_argument("--party", type=str, default="poker", help="The room to connect to")
parser.add_argument("--key", type=str, default="", help="The key for authentication")
parser.add_argument("--simulations", type=int, default=900)

args = parser.parse_args()


def card_name(card: pokerTypes.Card):
    val = str(card.rank)
    if card.rank == 1:
        val = "A"
    if card.rank == 10:
        val = "T"
    elif card.rank == 11:
        val = "J"
    elif card.rank == 12:
        val = "Q"
    elif card.rank == 13:
        val = "K"
    return f"{val}{card.suit[0]}"


percentile_to_hands = defaultdict(list)
for hand, percentile in eval_hand_strength.poker_hand_percentiles.items():
    percentile_to_hands[percentile].append(hand)
sorted_percentiles = sorted(percentile_to_hands.keys())


class max_eric_bot(Bot):
    last_target_bet = 0
    fold_ = 0
    preflop_fold_ = 2
    call_ = 0
    raise_ = 0
    check_ = 0
    total_ = 0
    isFirstMove = True
    recently_raised = False
    round_count = 4
    villain_tolerance = 25
    raised = False
    rank_map = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "J",
        12: "Q",
        13: "K",
        1: "A",
    }

    def act(self, state, hand):
        #time.sleep(3)
        # check if rased and if big blind during pre-flop
        # if self.last_target_bet == state.target_bet and state.round == "pre-flop":
        #     self.raised = False
        #     state.target_bet = 0
        #     return {"type": "call"}
        if state.round == "pre-flop" and self.raised == False:
            #self.raised = False
            #state.target_bet = 0
            return {"type": "call"}
        #if not (self.raised):
            #return {"type": "call"}
        
        # parsing board into [('A', 'Diamond'), ('K', 'Diamond')] format into board_cards
        board_cards = []
        for card in state.cards:
            board_cards.append((self.rank_map[card.rank], card.suit.capitalize()))
        # hand_cards formatted in the same way
        hand_cards = [
            (self.rank_map[hand[0].rank], hand[0].suit.capitalize()),
            (self.rank_map[hand[1].rank], hand[1].suit.capitalize()),
        ]

        # print('asked to act')
        # print('acting', state, hand, self.my_id)
        #print(board_cards)
        if state.round != "pre-flop":
            hands = self.get_hands_in_percentile_range(self.preflop_fold_rate())
            all_parsed_hands = eval_hand_strength.parse_all_hands(hands)
            our_hand = hand_cards+board_cards
            rets = [eval_hand_strength.compare_hands(our_hand, h+board_cards) for h in all_parsed_hands]
            num_hands_evaluated = len(all_parsed_hands)
            win_chance = rets.count(1)/num_hands_evaluated
            loss_chance = rets.count(-1)/num_hands_evaluated
            tie_chance = rets.count(0)/num_hands_evaluated
            print("win chance from range", win_chance)
            print("loss chance from range", loss_chance)
            print("tie chance from range", tie_chance)
        else:
            win_chance = self.win_prob(state, hand)
            loss_chance = 1-win_chance
            tie_chance = 0
            print("win chance from treys", win_chance)
        #print(self.preflop_fold_rate())
        #print(hands, self.preflop_fold_rate())
        #print(len(eval_hand_strength.parse_all_hands(hands)))
        #p = self.win_prob(state, hand)
        p = win_chance
        EV_fold = 0
        EV_Call = p * (state.pot + state.target_bet) - (state.target_bet) * (1 - p)
        print("OUR HAND", hand_cards)
        print("POT", state.pot)
        print("Target bet", state.target_bet)
        print("fold rate", self.preflop_fold_rate())
        print("fold equity", win_chance*state.pot)
        print("win equity", tie_chance*(state.pot+100))
        print("loss equity", loss_chance*(100))
        print("EV of a call", EV_Call)
        best_bet_move = {"type": "raise", "amount": 0}
        best_bet_EV = -10000
        if EV_Call > 0:
            for bet_val in [10, 20, 30, 40, 50, state.pot, 2*state.pot, 3*state.pot]:
                EV_Bet = (-loss_chance*(bet_val)+win_chance*(state.pot+bet_val))
                print("EV of bet size", bet_val, ":", EV_Bet)
                if EV_Bet > best_bet_EV:
                    best_bet_move["amount"] = bet_val
                    best_bet_EV = EV_Bet
        print("EV of a best bet", best_bet_EV)
        print("===========================")
        moves = [0, EV_Call, best_bet_EV]
        best_move = moves.index(max(moves))
        
        if  best_move == 0:
            if not self.raised:
                self.raised = False
                print("WE CALL")
                return {"type": "call"}
            else:
                self.raised = False
                print("WE FOLD")
                return {"type": "fold"}
        elif  best_move == 1:
            self.raised = False
            print("WE CALL A BET")
            return {"type": "call"}
        else: 
            self.raised = False
            self.recently_raised = True
            print("WE RAISE")
            return best_bet_move

    def opponent_action(self, action, player):
        if action.type == "fold":
            self.fold_ += 1
        elif action.type == "call":
            self.call_ += 1
        elif action.type == "raise":
            self.raised = True
            self.raise_ += 1
            self.isFirstMove = False
        if self.recently_raised and self.isFirstMove:
            self.isFirstMove = False
            if action.type == "fold":
                self.preflop_fold_ += 1
        print("opponent action?", action, player)

    def game_over(self, payouts):
        print("game over", payouts)

    def start_game(self, my_id):
        self.recently_raised = False
        self.my_id = my_id
        print("start game", my_id)
        self.isFirstMove = True
        self.round_count += 1

    def win_prob(
        self,
        state: pokerTypes.PokerSharedState,
        hand: Tuple[pokerTypes.Card, pokerTypes.Card],
    ):
        out = 0
        hand = [treys.Card.new(card_name(hand[0])), treys.Card.new(card_name(hand[1]))]
        board = [treys.Card.new(card_name(card)) for card in state.cards]
        evaluator = treys.Evaluator()
        for i in range(args.simulations):
            deck = treys.Deck()
            deck.shuffle()
            for card in hand + board:
                deck.cards.remove(card)
            pred = board + deck.draw(5 - len(board))
            score = evaluator.evaluate(hand, pred)
            other = 10**9

            for player in state.players:
                if player.id != self.my_id:
                    other = min(other, evaluator.evaluate(deck.draw(2), pred))
            if score < other:
                out += 1
        return out / args.simulations

    def pot_odds(self, state: pokerTypes.PokerSharedState, ev: float) -> float:
        return (state.pot + state.target_bet) * ev - state.target_bet * (1 - ev)

    def get_hands_in_percentile_range(
        self, max_percentile: int, max_threshold=60
    ) -> list[str]:
        hands = []
        max_percentile = min(max_threshold, max_percentile)
        for percentile in sorted_percentiles:
            if percentile <= max_percentile:
                hands.extend(percentile_to_hands[percentile])
        return hands

    def get_player_max_percentile(self, player_id: str) -> int:
        return self.fold_.get(player_id, 15) / self.round_count

    def preflop_fold_rate(self):
      return (1-(self.preflop_fold_ / self.round_count)) * 100